"""Compare reviewed aggregate files without joining patient records or pooling medians."""
import argparse
import csv
from datetime import date
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import re
import sys
from plotly.offline import get_plotlyjs
from .contracts import assert_aggregate_payload
from .provenance import CALCULATION_SETTINGS

POPULATION = ('patients','fractions','technical_fractions','manual_fractions','treated_plans',
    'new_plans','treatment_days','patients_per_day','fractions_per_day','plan_ends_complete',
    'plan_ends_incomplete','plan_ends_target_unknown','plan_open_followup','plans_resumed_after_gap')
FLOW = ('completed_counselling_appointments','open_counselling_appointments',
    'cancelled_counselling_appointments','registered_counselling_appointments','counselling_episodes',
    'treatment_episodes','completed_treatment_episodes','multiple_counselling','mature_episodes',
    'matched_mature','observation_mature','unresolved_mature','provisional','unresolved_pct','cancellation_pct')
FLOW_PERIOD = ('treatment_starts','treatment_ends','counselling_episodes',
    'registered_counselling_appointments','completed_counselling_appointments',
    'open_counselling_appointments','cancelled_counselling_appointments')
KPI = ('visits','expected_visits','unique_patients','relevant_slots','matched_slots','measurable_slots',
    'booked_minutes','overlap_minutes_in_slots','duration_minutes_in_slots','slot_coverage_pct',
    'duration_ratio_pct','measured_visits_pct','complete_device_days','incomplete_device_days',
    'duration_mean','booked_mean','fallback_intervals','free_hours','free_gt30_hours','window_hours',
    'free_pct','free_gt30_pct','free_mean_hours','free_gt30_mean_hours','window_mean_hours')
DISTRIBUTIONS = ('duration','booked','slot_coverage','duration_ratio','cycle','change','free','free_gt30','free_pct')
IMAGE_KINDS = {'kv_cbct','mv_cbct','cbct_unknown','exactrac_2d','kv_2d','mv_2d','unknown_2d','unknown'}
IMAGE_VALUES = ('objects','denominator_visits','matched_objects','matched_visits',
    'objects_per_100_visits','visits_with_objects_pct')
FIELDS = {
    'throughput': {'source','event_start','event_end','activity_start','activity_end','completed',
                   'plan_key','fraction','time_source'},
    'population': {'source','event_start','plan_key','fraction','patient_class','planned_fractions','plan_first_treatment'},
    'flow': {'source','event_start','event_end','milestone_time','patient_class','activity_name'},
    'imaging': {'source','event_start','image_kind','image_seconds','image_time_source'},
}
ALIASES = re.compile(r'[A-Za-z0-9][A-Za-z0-9_. -]{0,47}\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')
MODELS = {'activity','workflow','technical'}
GRANULARITIES = {'year','quarter','month','week'}
DOMAIN_LABELS = {'throughput':'Durchsatz','population':'Patienten / Behandlung',
                'flow':'Aufklaerung / Episoden','imaging':'Bildobjekte'}
REVIEW_GUIDANCE = {
    'period_mismatch': ('Unterschiedliche Gesamtzeitraeume', 'Dasselbe Beobachtungsjahr auswerten; abweichende Jahre getrennt berichten.'),
    'local_review_missing': ('Lokale Vergleichspruefung fehlt', 'Zuordnungen, Positiv-/Negativfaelle und Nenner lokal pruefen; erst danach --reviewed verwenden.'),
    'observation_incomplete': ('Gesamtzeitraum nicht vollstaendig beobachtet', 'Vollstaendigen Zeitraum exportieren oder einen kuerzeren gemeinsamen Zeitraum gesondert definieren.'),
    'synthetic_mixed': ('Synthetische und klinische Daten gemischt', 'Demo- und Klinikdateien in getrennten Vergleichen auswerten.'),
    'profile_unconfirmed': ('Standortprofil nicht bestaetigt', 'Terminarten, Status, Therapiegeraete sowie Brachy/manuelle Therapien lokal pruefen und das Profil bestaetigen.'),
    'coverage_unconfirmed': ('Quellenumfang / Datenstand nicht bestaetigt', 'Quellenumfang und vollstaendigen Datenstand lokal pruefen; sources_complete und complete_through nicht aus dem letzten Ereignis erraten.'),
    'provenance_missing': ('Herkunftsmetadaten fehlen', 'Vorhandenen vollstaendigen Export mit der aktuellen Analyse neu berechnen; keine Herkunftsangaben nachtragen.'),
    'provenance_incomplete': ('Herkunftsmetadaten unvollstaendig', 'Vorhandenen Export mit der aktuellen Analyse neu berechnen; bei fehlenden Quelldaten neu exportieren.'),
    'collector_missing': ('RDL-Exportstand unbekannt', 'Mit demselben dokumentierten Full-Collector-RDL neu als Excel exportieren. Metadaten nicht manuell ersetzen.'),
    'collector_mismatch': ('Unterschiedliche RDL-Exportstaende', 'Standorte mit demselben geprueften Full-Collector-RDL exportieren. Gleiche Python-Version allein gleicht SQL-Unterschiede nicht aus.'),
    'collector_resources_legacy': ('Alter Ressourcenabgleich im RDL', 'RDL vor rc.6 kann parallele Reservierungen zusammenfassen oder durch inaktive Ressourcen fehlzuordnen. Fuer den vollstaendigen Abgleich mit rc.6 oder neuer neu exportieren; Python kann verlorene Zuordnungen nicht wiederherstellen.'),
    'analysis_mismatch': ('Unterschiedlicher Rechenstand', 'Beide vorhandenen Exporte mit demselben Analysepaket neu berechnen; kein neuer RDL-Lauf allein wegen dieses Unterschieds.'),
    'settings_mismatch': ('Unterschiedliche Recheneinstellungen', 'Patientenfilter, Zeitfenster und Besuchstoleranzen gemeinsam festlegen und neu berechnen; Standortzuordnungen bleiben lokal.'),
    'dependencies_mismatch': ('Unterschiedliche Bibliotheksversionen', 'Exporte in derselben Python-Umgebung mit denselben Abhaengigkeiten neu berechnen.'),
    'contract_mismatch': ('Unterschiedliche Exportvertraege', 'Denselben unterstuetzten Full Collector verwenden und neu exportieren.'),
    'contract_unsupported': ('Nicht unterstuetzter Exportvertrag', 'Full Collector mit Exportvertrag 2.0 verwenden; Altdateien bleiben nur deskriptiv.'),
    'capabilities_missing': ('Quelleninventar fehlt', 'Full Collector als Excel einschliesslich 01_Capabilities exportieren. Eine reine Ereignis-CSV belegt das Quelleninventar nicht.'),
    'required_source_missing': ('Erforderliche Quelle fehlt', 'Fehlende Tabellen/Felder und Leserechte mit der lokalen ARIA-Administration pruefen; danach erneut exportieren.'),
    'capabilities_mismatch': ('Unterschiedliche Quellenverfuegbarkeit', 'Inventare und Leserechte vergleichen. Fehlende optionale Quellen explizit ausweisen, nicht durch Nullen ersetzen.'),
    'fields_missing': ('Erforderliche Datenfelder fehlen', 'Neueren Full Collector verwenden und pruefen, ob die benoetigten Felder lokal verfuegbar sind.'),
    'context_mismatch': ('Unterschiedlicher Vorlauf', 'Mit gleichem Vorlauf neu exportieren, damit laufende Plaene und Episoden am Jahresbeginn gleich eingeordnet werden.'),
    'context_missing': ('Vorlauf nicht dokumentiert', 'Vollstaendigen Export mit dokumentiertem Kontextbeginn verwenden; nicht aus dem ersten beobachteten Ereignis ableiten.'),
    'followup_missing': ('Nachbeobachtungsstand fehlt', 'Datenstand und erforderliche Nachbeobachtung lokal pruefen und dokumentiert exportieren.'),
    'followup_mismatch': ('Unterschiedliche Nachbeobachtung', 'Fuer Episoden einen gemeinsamen Datenstichtag festlegen und entsprechend neu exportieren; Durchsatz im abgeschlossenen Jahr bleibt separat beurteilbar.'),
    'flow_sources_unconfirmed': ('Patientenflussquellen nicht bestaetigt', 'Insbesondere Behandlungen ohne R&V, Brachy und Wiedervorstellungen pruefen. Kein fehlender Start allein wegen einer fehlenden Quelle.'),
    'imaging_unavailable': ('Direkte Bildobjekte nicht verfuegbar', 'Bildobjektquelle und Leserechte pruefen. Technische Imaging-Nachweise nicht als vollstaendige Bildobjektfrequenz ausgeben.'),
    'pool_missing': ('Kein Standortpool', 'Pruefen, ob fuer diesen Abschnitt und dieses Modell ausreichend messbare Besuche vorhanden sind.'),
    'suppressed_group': ('Standortpool unterdrueckt', 'Kleine Gruppen nicht rekonstruieren. Gegebenenfalls einen groesseren, gemeinsam definierten Zeitraum betrachten.'),
    'partial_period': ('Unvollstaendiger Abschnitt', 'Nur gleich abgegrenzte vollstaendige Abschnitte vergleichen; Teilperioden gesondert kennzeichnen.'),
    'partial_population': ('Pool enthaelt nicht alle Geraete', 'Unterdrueckte oder nicht messbare Geraete pruefen; den Teilpool nicht als gesamten Standort interpretieren.'),
    'incomplete_device_days': ('Freie Zeit nur fuer vollstaendig messbare Geraetetage', 'Fehlende Zeitintervalle und Modellabdeckung pruefen. Freie Stunden und deren Anteil gelten nur fuer die vollstaendigen Geraetetage im Nenner, nicht als Jahresauslastung oder Hochrechnung auf alle Tage.'),
    'denominator_missing': ('Exakte Nenner fehlen', 'Mit der aktuellen Analyse neu berechnen. Unterdrueckte Nenner bleiben fehlend und werden nicht rueckgerechnet.'),
    'period_missing': ('Abschnitt nicht vorhanden', 'Zeitraum, Datenabdeckung und Modell pruefen. Fehlende Abschnitte sind keine Nullwerte.'),
}


def _numeric(value):
    if value is None:
        return None
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0:
        raise ValueError('Invalid numeric aggregate')
    return value


def _numbers(source, fields, suppressed=False):
    return {key:None if suppressed else _numeric(source.get(key)) for key in fields}


def _distribution(source):
    if source.get('suppressed',False):
        return {}
    result = _numbers(source,('n','patients','low','q1','median','q3','high'))
    quartiles = [result[k] for k in ('q1','median','q3')]
    if all(v is not None for v in quartiles) and quartiles != sorted(quartiles):
        raise ValueError('Invalid numeric quantiles')
    return result


def _date(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
        raise ValueError('Invalid period')
    date.fromisoformat(value)
    return value


def _fingerprint(value):
    return value if isinstance(value,str) and HEX.fullmatch(value) else None


def _version(value):
    return value if isinstance(value,str) and re.fullmatch(r'[0-9A-Za-z.+_-]{1,48}',value) else 'unknown'


def _collector_release(value):
    return value if (isinstance(value,str) and len(value) <= 48
                     and re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?',value)) else None


def _periods(data):
    for granularity, models in data.get('periods',{}).items():
        if granularity not in GRANULARITIES:
            continue
        for model, periods in models.items():
            if model not in MODELS:
                continue
            seen = set()
            for period in periods:
                start,end = _date(period['start']),_date(period['end'])
                if start > end or (start,end) in seen:
                    raise ValueError('Duplicate or invalid period')
                seen.add((start,end))
                yield granularity,model,start,end,period


def _common_reasons(a,b,reviewed_a,reviewed_b):
    reasons = []
    if (a['start'],a['end']) != (b['start'],b['end']):
        reasons.append('period_mismatch')
    if not reviewed_a or not reviewed_b:
        reasons.append('local_review_missing')
    if any(not d.get('data_through') or d['data_through'] < d['end'] for d in [a,b]):
        reasons.append('observation_incomplete')
    if (a.get('synthetic') is True or a.get('provenance',{}).get('synthetic') is True) != (
        b.get('synthetic') is True or b.get('provenance',{}).get('synthetic') is True):
        reasons.append('synthetic_mixed')
    for field,reason in [('profile_confirmed','profile_unconfirmed'),
                         ('source_coverage_confirmed','coverage_unconfirmed')]:
        if a.get('quality',{}).get(field) is not True or b.get('quality',{}).get(field) is not True:
            reasons.append(reason)
    pa,pb = a.get('provenance'),b.get('provenance')
    if not isinstance(pa,dict) or not isinstance(pb,dict):
        return reasons + ['provenance_missing']
    releases = [_collector_release(p.get('collector_release')) for p in [pa,pb]]
    if any(release is None for release in releases):
        reasons.append('collector_missing')
    if releases[0] != releases[1]:
        reasons.append('collector_mismatch')
    # Reanalysis cannot undo source-level appointment/resource grouping in old exports.
    if any(re.fullmatch(r'2\.0\.0-rc\.[1-5]',release or '') for release in releases):
        reasons.append('collector_resources_legacy')
    for p in [pa,pb]:
        if (p.get('schema') != 1 or not _fingerprint(p.get('analysis_sha256'))
            or not _fingerprint(p.get('export_sha256'))
            or not set(CALCULATION_SETTINGS) <= set(p.get('settings',{}))
            or not {'numpy','pandas'} <= set(p.get('dependencies',{}))):
            reasons.append('provenance_incomplete')
        if not p.get('capabilities'):
            reasons.append('capabilities_missing')
        if any(c.get('required') is True and c.get('available') is not True for c in p.get('capabilities',[])):
            reasons.append('required_source_missing')
    for key,reason in [('analysis_sha256','analysis_mismatch'),('contract_version','contract_mismatch'),
                       ('settings','settings_mismatch'),('dependencies','dependencies_mismatch')]:
        if pa.get(key) != pb.get(key):
            reasons.append(reason)
    if pa.get('contract_version') != '2.0' or pb.get('contract_version') != '2.0':
        reasons.append('contract_unsupported')
    caps = lambda p: sorted((str(c.get('source','')),str(c.get('column','')),c.get('available') is True)
                            for c in p.get('capabilities',[]))
    if caps(pa) != caps(pb):
        reasons.append('capabilities_mismatch')
    return sorted(set(reasons))


def _domains(a,b,reviewed_a,reviewed_b):
    common = _common_reasons(a,b,reviewed_a,reviewed_b)
    pa,pb = a.get('provenance') or {},b.get('provenance') or {}
    result = {}
    for domain, required in FIELDS.items():
        reasons = list(common)
        if any(not required <= set(p.get('fields',[])) for p in [pa,pb]):
            reasons.append('fields_missing')
        if domain in {'flow','population'} and pa.get('context_start') != pb.get('context_start'):
            reasons.append('context_mismatch')
        if domain in {'flow','population'} and any(not p.get('context_start') for p in [pa,pb]):
            reasons.append('context_missing')
        if domain == 'flow':
            if not a.get('data_through') or not b.get('data_through'):
                reasons.append('followup_missing')
            elif a['data_through'] != b['data_through']:
                reasons.append('followup_mismatch')
            if a.get('flow',{}).get('sources_complete') is not True or b.get('flow',{}).get('sources_complete') is not True:
                reasons.append('flow_sources_unconfirmed')
        if domain == 'imaging' and (a.get('imaging',{}).get('available') is not True
                                   or b.get('imaging',{}).get('available') is not True):
            reasons.append('imaging_unavailable')
        result[domain] = dict(compatible=not reasons,reasons=sorted(set(reasons)))
    return result


def build_comparison(sites, reviewed=frozenset()):
    if not 2 <= len(sites) <= 12:
        raise ValueError('Comparison needs 2 to 12 sites')
    if set(reviewed)-set(sites):
        raise ValueError('Unknown reviewed alias')
    aliases = set()
    fingerprints = set()
    output = dict(schema=1,sites=[],periods=[],clinical_periods=[],imaging=[],checks=[])
    for alias,data in sites.items():
        if not ALIASES.fullmatch(alias) or alias.casefold() in aliases:
            raise ValueError('Invalid or duplicate alias')
        aliases.add(alias.casefold())
        assert_aggregate_payload(data)
        start,end = _date(data['start']),_date(data['end'])
        if start > end:
            raise ValueError('Invalid period')
        if data.get('data_through'):
            _date(data['data_through'])
        try:
            source_hash = hashlib.sha256(json.dumps(data,sort_keys=True,allow_nan=False).encode()).hexdigest()
        except ValueError:
            raise ValueError('Invalid numeric aggregate') from None
        provenance = data.get('provenance') or {}
        identities = {('aggregate',source_hash)}
        for key in ['export_sha256','run_sha256']:
            digest = _fingerprint(provenance.get(key))
            if digest:
                identities.add((key,digest))
        if identities & fingerprints:
            raise ValueError('Duplicate submission or source run')
        fingerprints.update(identities)
        output['sites'].append(dict(alias=alias,start=start,end=end,data_through=data.get('data_through'),
            synthetic=data.get('synthetic') is True or provenance.get('synthetic') is True,
            reviewed=alias in reviewed,profile_confirmed=data.get('quality',{}).get('profile_confirmed') is True,
            coverage_confirmed=data.get('quality',{}).get('source_coverage_confirmed') is True,
            provenance_available=bool(provenance),analysis_sha256=_fingerprint(provenance.get('analysis_sha256')),
            export_sha256=_fingerprint(provenance.get('export_sha256')),aggregate_sha256=source_hash,
            version=_version(data.get('version')),
            collector_release=_collector_release(provenance.get('collector_release')) or 'unknown',
            context_start=_date(provenance['context_start']) if provenance.get('context_start') else None,
            capability_count=len(provenance.get('capabilities',[])),
            available_capability_count=sum(c.get('available') is True for c in provenance.get('capabilities',[])),
            population=_numbers(data.get('population',{}).get('summary',{}),POPULATION),
            flow=_numbers(data.get('flow',{}),FLOW)))
        for granularity,model,a,b,period in _periods(data):
            pools = [g for g in period.get('groups',[]) if g.get('machine') == 'ALL']
            if len(pools)>1:
                raise ValueError('Duplicate aggregate pool')
            pool = pools[0] if pools else {}
            suppressed = pool.get('suppressed',True) is not False
            reasons = []
            if not pools:
                reasons.append('pool_missing')
            if suppressed:
                reasons.append('suppressed_group')
            if period.get('partial'):
                reasons.append('partial_period')
            if pool.get('pool_excludes_suppressed'):
                reasons.append('partial_population')
            kpi = _numbers(pool.get('kpi',{}),KPI,suppressed)
            if any(kpi[k] is None for k in ['expected_visits','booked_minutes','overlap_minutes_in_slots']):
                reasons.append('denominator_missing')
            if kpi['incomplete_device_days'] is not None and kpi['incomplete_device_days'] > 0:
                reasons.append('incomplete_device_days')
            output['periods'].append(dict(alias=alias,granularity=granularity,model=model,start=a,end=b,
                label=a+' / '+b,kpi=kpi,distributions={} if suppressed else {
                    key:_distribution(value) for key,value in pool.get('distributions',{}).items()
                    if key in DISTRIBUTIONS},reasons=reasons))
        for domain,fields,values_key in [('population',POPULATION,'current'),('flow',FLOW_PERIOD,'values')]:
            for granularity,periods in data.get(domain,{}).get('periods',{}).items():
                if granularity not in GRANULARITIES:
                    continue
                seen = set()
                for period in periods:
                    a = _date(period['start'])
                    if a in seen:
                        raise ValueError('Duplicate clinical period')
                    seen.add(a)
                    output['clinical_periods'].append(dict(alias=alias,domain=domain,granularity=granularity,
                        start=a,values=_numbers(period.get(values_key,{}),fields)))
        imaging = data.get('imaging') or {}
        image_periods = list(_periods(imaging))
        machines = sorted({str(g.get('machine','')) for *_,p in image_periods for g in p.get('groups',[])})
        devices = {name:f'{alias}-D{i+1}' for i,name in enumerate(machines)}
        equipment = {machine:sorted({str(g.get('equipment','')) for *_,p in image_periods
                        for g in p.get('groups',[]) if str(g.get('machine','')) == machine}) for machine in machines}
        for granularity,model,a,b,period in image_periods:
            for g in period.get('groups',[]):
                output['imaging'].append(dict(alias=alias,granularity=granularity,model=model,start=a,end=b,
                    device=devices[str(g.get('machine',''))],
                    epoch=equipment[str(g.get('machine',''))].index(str(g.get('equipment','')))+1,
                    kind=g.get('kind') if g.get('kind') in IMAGE_KINDS else 'unknown',
                    values=_numbers(g,IMAGE_VALUES),exposure_seconds=_distribution(g.get('exposure_seconds',{})),
                    visit_duration_minutes=_distribution(g.get('visit_duration_minutes',{}))))
    for (alias_a,a),(alias_b,b) in combinations(sites.items(),2):
        output['checks'].append(dict(a=alias_a,b=alias_b,
            domains=_domains(a,b,alias_a in reviewed,alias_b in reviewed)))
    reasons = {reason for check in output['checks'] for domain in check['domains'].values()
               for reason in domain['reasons']}
    reasons.update(reason for period in output['periods'] for reason in period['reasons'])
    output['review_actions'] = [dict(reason=reason,label=REVIEW_GUIDANCE[reason][0],
                                    action=REVIEW_GUIDANCE[reason][1]) for reason in sorted(reasons)]
    return output


def write_outputs(data, output):
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    assert_aggregate_payload(data)
    serialized = json.dumps(data,ensure_ascii=True,allow_nan=False)
    (output/'Vergleich.json').write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
    escaped = serialized.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template = Path(__file__).with_name('comparison.html').read_text(encoding='utf-8')
    (output/'Standortvergleich.html').write_text(template.replace('__PLOTLY__',get_plotlyjs())
        .replace('__COMPARISON_DATA__',escaped),encoding='utf-8')
    notes = ['# Pruefhinweise zum Standortvergleich', '',
             'Automatisch aus den vorliegenden Aggregaten; keine klinische Freigabe.', '',
             '| Standort | RDL | Analyse | Kontext ab | Daten bis | Quellenfelder verfuegbar / im Inventar |',
             '| --- | --- | --- | --- | --- | --- |']
    for site in data['sites']:
        notes.append(f"| {site['alias']} | {site['collector_release']} | {site['version']} | "
                     f"{site['context_start'] or '--'} | {site['data_through'] or '--'} | "
                     f"{site['available_capability_count']} / {site['capability_count']} |")
    notes += ['', '## Offene Voraussetzungen je Standortpaar', '']
    for check in data['checks']:
        for domain,result in check['domains'].items():
            reasons = '; '.join(REVIEW_GUIDANCE[r][0] for r in result['reasons'])
            notes.append(f"- {check['a']} / {check['b']}, {DOMAIN_LABELS[domain]}: "
                         +(reasons or 'Methodische Voraussetzungen dokumentiert; keine klinische Freigabe.'))
    notes += ['', '## Naechste Schritte', '']
    notes += [f"- **{item['label']}:** {item['action']}" for item in data['review_actions']]
    notes += ['', 'Neue oder korrigierte Quellen ergeben eine neue Einreichungsrevision. '
              'Die alte Lieferung nicht als weiteren Standort zaehlen. '
              'Auch bei gleichem Rechenstand bleiben lokale Fallpruefung, '
              'Fallmix und Freigabe fuer eine Publikation erforderlich.', '']
    (output/'Pruefhinweise.md').write_text('\n'.join(notes),encoding='utf-8')
    with (output/'Standorte.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer = csv.writer(stream,delimiter=';')
        writer.writerow(['Standort','Von','Bis','Domaene','Kennzahl','Wert','Lokal_geprueft'])
        for site in data['sites']:
            for domain in ['population','flow']:
                for name,value in site[domain].items():
                    writer.writerow([site['alias'],site['start'],site['end'],domain,name,value,site['reviewed']])
    with (output/'Perioden.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        fields = ['alias','granularity','model','start','end',*KPI]
        writer = csv.DictWriter(stream,fieldnames=fields,delimiter=';')
        writer.writeheader()
        for period in data['periods']:
            writer.writerow({**{k:period[k] for k in fields[:5]},**period['kpi']})


def main(argv=None):
    parser = argparse.ArgumentParser(description='Lokaler Vergleich aggregierter Standorte; keine Patientendaten.')
    parser.add_argument('--site',action='append',required=True,metavar='ALIAS=aggregate.json')
    parser.add_argument('--reviewed',action='append',default=[],metavar='ALIAS')
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(argv)
    sites = {}
    for item in args.site:
        alias,separator,path = item.partition('=')
        if not separator or alias in sites:
            raise ValueError('Invalid or duplicate alias')
        source = Path(path)
        if source.stat().st_size > 128*1024*1024:
            raise ValueError('Aggregate file too large')
        sites[alias] = json.loads(source.read_text(encoding='utf-8-sig'))
    data = build_comparison(sites,reviewed=set(args.reviewed))
    write_outputs(data,args.output)
    print(f'COMPARISON_OK sites={len(sites)} pairs={len(data["checks"])}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,KeyError,OSError,TypeError,RecursionError):
        print('COMPARISON_REFUSED: Aggregate, Aliasse und Metadaten lokal pruefen.',file=sys.stderr)
        sys.exit(2)
