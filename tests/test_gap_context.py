import pandas as pd
from analysis.gap_context import collect, publish
from analysis.throughput import prepare_visits
from analysis.contracts import Profile


def test_gap_threshold_includes_exactly_30_and_deduplicates_appointment():
    rows=pd.DataFrame([dict(event_start=pd.Timestamp('1970-01-01 00:01'),
         event_end=pd.Timestamp('1970-01-01 02:00'),activity_code='QA',kind='block',patient_key='')])
    result={}
    collect(rows,[(0,30),(40,69),(80,111)],result)
    out=publish(result,5,True)[0]
    assert out['appointments']==1 and out['overlap_minutes']==60
    assert publish(result,5,False)[0]['appointments'] is None


def test_actual_activity_end_is_not_scheduled_end():
    common=dict(patient_key='p',machine='M',plan_key='P',fraction=1,status='completed')
    rows=pd.DataFrame([
        dict(common,source='delivery',event_key='d',activity_code='',event_start='2025-01-02 08:05',event_end='2025-01-02 08:10'),
        dict(common,source='appointment',event_key='a',activity_code='TX',event_start='2025-01-02 08:00',event_end='2025-01-02 09:00',
             activity_start='2025-01-02 08:02',activity_end='2025-01-02 08:15',completed='2025-01-02 08:16')])
    result=prepare_visits(rows,Profile(machines={'M':'Linac'},activity_codes={'TX':'treatment_external'}))
    activity=result['visits']['activity'].iloc[0]
    assert activity.duration==13 and activity.booked==60 and activity.overlap==13
    assert result['visits']['workflow'].iloc[0].duration==10
