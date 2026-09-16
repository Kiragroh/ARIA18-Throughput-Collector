import pandas as pd
import pytest

from analysis.contracts import Profile
from analysis.throughput import prepare_visits, aggregate


def rows():
    return [
        dict(source='delivery',event_key='beam',patient_key='p',machine='M',plan_key='plan',fraction=1,
             event_start='2025-01-02 08:05',event_end='2025-01-02 08:10',status='delivered',activity_code=''),
        dict(source='imaging',event_key='image',patient_key='p',machine='M',plan_key='plan',fraction=1,
             event_start='2025-01-02 08:03',event_end='2025-01-02 08:04',status='completed',activity_code=''),
        dict(source='appointment',event_key='slot',patient_key='p',machine='M',activity_code='LOCAL',
             event_start='2025-01-02 08:00',event_end='2025-01-02 08:20',
             activity_start='2025-01-02 08:01',activity_end='2025-01-02 08:15',status='completed'),
    ]


def profile(**kwargs):
    return Profile(machines={'M':'Machine'},**kwargs)


def test_unknown_name_uses_unambiguous_contained_technical_evidence_for_timing_only():
    data=pd.DataFrame(rows())
    original=data.copy(deep=True)
    p=profile()
    prepared=prepare_visits(data,p)
    assert prepared['audit']['inferred_timing_slots'] == 1
    assert prepared['audit']['relevant_slots'] == 1
    assert prepared['audit']['matched_slots'] == 1
    assert prepared['visits']['activity'].iloc[0].duration == 14
    assert prepared['visits']['workflow'].iloc[0].duration == 12
    assert prepared['visits']['technical'].iloc[0].duration == 7
    assert p.classify_activities(data).eq('unknown').all()
    pd.testing.assert_frame_equal(data,original)


@pytest.mark.parametrize('changes', [
    {'machine':'OTHER'}, {'patient_key':'different'}, {'patient_key':None},
    {'activity_start':None}, {'activity_end':None},
    {'activity_start':'2025-01-02 08:06'}, {'activity_end':'2025-01-02 08:09'},
    {'activity_start':'2025-01-02 04:00'}, {'activity_end':'2025-01-03 08:15'},
    {'event_end':None}, {'event_end':'2025-01-02 07:59'},
    {'event_start':'2025-01-02 01:00'}, {'status':'cancelled'}, {'status':'deleted'}, {'status':'unclassified'},
])
def test_unsupported_unknown_appointments_are_not_recovered(changes):
    data=rows()
    data[-1].update(changes)
    result=prepare_visits(pd.DataFrame(data),profile())
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['visits']['workflow'].empty


@pytest.mark.parametrize('kind',['ignore','block','observation','counselling'])
def test_explicit_nontherapy_classification_is_never_overridden(kind):
    result=prepare_visits(pd.DataFrame(rows()),profile(activity_codes={'LOCAL':kind}))
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['visits']['workflow'].empty


def test_declared_therapy_has_priority_and_ambiguous_declared_matches_block_recovery():
    data=rows()
    declared={**data[-1],'event_key':'declared','activity_code':'TX','event_start':'2025-01-02 07:59'}
    data.append(declared)
    result=prepare_visits(pd.DataFrame(data),profile(activity_codes={'TX':'treatment_external'}))
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['audit']['matched_slots'] == 1
    data.append({**declared,'event_key':'declared2','activity_code':'TX2'})
    result=prepare_visits(pd.DataFrame(data),profile(activity_codes={'TX':'treatment_external','TX2':'treatment_external'}))
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['visits']['workflow'].empty


def test_two_unknown_appointments_or_two_technical_visits_do_not_get_arbitrary_winners():
    data=rows()
    data.append({**data[-1],'event_key':'other','activity_code':'OTHER'})
    result=prepare_visits(pd.DataFrame(data),profile())
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['audit']['ambiguous_inferred_timing_slots'] == 2
    data=rows()
    data[-1]['activity_end']='2025-01-02 08:55'
    data.append({**data[0],'event_key':'beam2','plan_key':'plan2',
                 'event_start':'2025-01-02 08:45','event_end':'2025-01-02 08:50'})
    result=prepare_visits(pd.DataFrame(data),profile())
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['audit']['ambiguous_inferred_timing_slots'] == 1


def test_only_unknown_timing_is_recovered_not_a_missing_delivery():
    data=pd.DataFrame(rows()[1:])
    result=prepare_visits(data,profile())
    assert result['audit']['inferred_timing_slots'] == 0
    assert result['visits']['activity'].empty


def test_open_status_with_documented_interval_and_actual_delivery_does_not_change_status():
    data=rows()
    data[-1]['status']='open'
    frame=pd.DataFrame(data)
    result=prepare_visits(frame,profile())
    assert result['audit']['inferred_timing_slots'] == 1
    assert frame.iloc[-1].status == 'open'


def test_input_order_does_not_resolve_or_create_inferred_matches():
    data=pd.DataFrame(rows())
    for shuffled in [data.iloc[::-1],data.sample(frac=1,random_state=17)]:
        result=prepare_visits(shuffled,profile())
        assert result['audit']['inferred_timing_slots'] == 1
        assert result['visits']['workflow'].iloc[0].duration == 12


def test_recovered_slots_are_counted_per_period_with_small_subgroups_suppressed():
    data=[]
    for i in range(6):
        for row in rows():
            data.append({**row,'event_key':row['event_key']+str(i),'patient_key':str(i)})
    p=profile()
    result=aggregate(prepare_visits(pd.DataFrame(data),p),p)['year']['activity'][0]['groups'][-1]
    assert result['kpi']['inferred_timing_slots'] == 6
    assert result['kpi']['relevant_slots'] == 6
    assert result['kpi']['expected_visits'] == 6
    for row in data:
        if row['source']=='appointment' and row['patient_key']!='0':
            row['activity_code']='TX'
    p=profile(activity_codes={'TX':'treatment_external'})
    result=aggregate(prepare_visits(pd.DataFrame(data),p),p)['year']['activity'][0]['groups'][-1]
    assert result['kpi']['inferred_timing_slots'] is None
    assert result['kpi']['relevant_slots'] == 6
