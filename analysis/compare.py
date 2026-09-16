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
