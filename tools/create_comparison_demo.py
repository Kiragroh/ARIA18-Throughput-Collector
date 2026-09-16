"""Fabricated six-site aggregate fixtures. No clinical file is read."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis.compare import build_comparison, write_outputs, FIELDS
from analysis.contracts import Profile
from analysis.provenance import CALCULATION_SETTINGS, analysis_digest


def create(output):
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    sites = {}
    for i in range(6):
        alias=f'DEMO-{i+1}'
        profile=Profile()
        data=dict(synthetic=True,version='2.0.0-demo',site=alias,start='2025-01-01',end='2025-12-31',
            data_through='2026-04-01',quality=dict(profile_confirmed=True,source_coverage_confirmed=True),
            provenance=dict(schema=1,synthetic=True,export_sha256=hashlib.sha256(alias.encode()).hexdigest(),
                run_sha256=hashlib.sha256(('run-'+alias).encode()).hexdigest(),analysis_sha256=analysis_digest(),
                contract_version='2.0',collector_release='2.0.0-demo',context_start='2024-01-01',
                fields=sorted(set().union(*FIELDS.values())),settings={k:getattr(profile,k) for k in CALCULATION_SETTINGS},
                capabilities=[dict(source='SYNTHETIC',column='SyntheticOnly',required=True,available=True)],
                dependencies={'numpy':'synthetic','pandas':'synthetic'}),
            population=dict(summary={},periods={}),flow=dict(sources_complete=True,periods={}),
            imaging=dict(available=True,periods={}),periods={})
        for granularity,freq,scale in [('month','M',1),('quarter','Q',3),('year','Y',12)]:
            data['periods'][granularity]={m:[] for m in ['activity','workflow','technical']}
            data['population']['periods'][granularity]=[]
            data['flow']['periods'][granularity]=[]
            data['imaging']['periods'][granularity]={m:[] for m in ['activity','workflow','technical']}
            for j,period in enumerate(pd.period_range('2025-01-01','2025-12-31',freq=freq)):
                a,b=str(period.start_time.date()),str(period.end_time.date())
                population=dict(patients=200*scale+i*20,fractions=600*scale+i*40,
                    technical_fractions=550*scale+i*40,manual_fractions=50*scale,
                    treated_plans=230*scale+i*10,new_plans=210*scale+i*10,treatment_days=20*scale,
                    patients_per_day=28+i,fractions_per_day=(600*scale+i*40)/(20*scale))
                data['population']['periods'][granularity].append(dict(start=a,end=b,current=population))
                flow=dict(treatment_starts=190*scale+i*8,treatment_ends=185*scale+i*8,
                    counselling_episodes=220*scale+i*9,completed_counselling_appointments=230*scale+i*9,
                    cancelled_counselling_appointments=20*scale,registered_counselling_appointments=255*scale+i*9,
                    open_counselling_appointments=5*scale)
                data['flow']['periods'][granularity].append(dict(start=a,values=flow))
                if granularity=='year':
                    data['population']['summary']=population
                    data['flow'].update({**flow,'treatment_episodes':flow['treatment_starts'],
                        'mature_episodes':flow['counselling_episodes'],'unresolved_mature':200+i*10,
                        'unresolved_pct':100*(200+i*10)/flow['counselling_episodes']})
                for m,model in enumerate(['activity','workflow','technical']):
                    n=500*scale+i*30
                    median=10+i*.6+m*1.5+(j%4)*.3
                    def dist(value, maximum=None):
                        return dict(suppressed=False,n=n,patients=population['patients'],
                            low=value*.5,q1=value*.8,median=value,q3=value*1.2,
                            high=min(value*1.5,maximum) if maximum is not None else value*1.5)
                    booked=n*20
                    overlap=booked*(.6+i*.02)
                    kpi=dict(visits=n,expected_visits=n+20,unique_patients=population['patients'],
                        relevant_slots=n+20,matched_slots=n,measurable_slots=n,booked_minutes=booked,
                        overlap_minutes_in_slots=overlap,duration_minutes_in_slots=n*median,
                        slot_coverage_pct=100*overlap/booked,duration_ratio_pct=100*n*median/booked,
                        measured_visits_pct=100*n/(n+20),complete_device_days=40*scale,
                        incomplete_device_days=5*scale,free_hours=80*scale,window_hours=320*scale,
                        free_pct=25,free_mean_hours=2,window_mean_hours=8)
                    data['periods'][granularity][model].append(dict(label=str(period),start=a,end=b,partial=False,
                        groups=[dict(machine='ALL',suppressed=False,pool_excludes_suppressed=False,kpi=kpi,
                            distributions={key:dist(value,100 if key=='slot_coverage' else None) for key,value in [('duration',median),('slot_coverage',60+i*2),
                                ('booked',20),('cycle',median+3),('change',3),('free',2),('free_gt30',1)]})]))
                    data['imaging']['periods'][granularity][model].append(dict(start=a,end=b,groups=[
                        dict(machine='Device',equipment='SYNTHETIC',kind=kind,objects=n*2,matched_objects=n,
                            denominator_visits=n,matched_visits=n//2,objects_per_100_visits=100,
                            visits_with_objects_pct=50,exposure_seconds=dist(8),visit_duration_minutes=dist(median))
                        for kind in ['kv_cbct','kv_2d']]))
        sites[alias]=data
        (output/(alias+'.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
    write_outputs(build_comparison(sites,reviewed=set(sites)),output/'Vergleich')
    print('SYNTHETIC_COMPARISON_OK sites=6')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    create(parser.parse_args().output)
