import pandas as pd
from analysis.contracts import Profile
from analysis.throughput import aggregate


def sample(expected=6, overlap=False):
    visits = pd.DataFrame([dict(machine='Linac', date='2025-01-02', patient_key=str(i),
        start=pd.Timestamp(f'2025-01-02 08:{i*10:02}'),
        end=pd.Timestamp(f'2025-01-02 08:{i*10+ (15 if overlap else 8):02}'),
        booked=10., overlap=8., duration=8., fallback=0) for i in range(5)])
    return dict(visits={'activity': visits}, expected={('Linac','2025-01-02'):expected},
        slots=pd.DataFrame(columns=['machine','date','matched','patient_key']),
        blocks=pd.DataFrame(columns=['machine','date']))


def result(expected=6, overlap=False):
    return aggregate(sample(expected, overlap), Profile(start='2025-01-02',end='2025-01-02',
        machines={'M':'Linac'},minimum_patients=5))['quarter']['activity'][0]['groups'][0]


def test_incomplete_day_retains_observed_transitions_not_idle_time():
    group=result()
    assert group['distributions']['cycle']['median']==10
    assert group['distributions']['change']['median']==2
    assert group['kpi']['free_hours'] is None
    assert group['distributions']['cycle_complete_days']['n'] is None
    assert group['transition_scope']=='consecutive_observed_visits'


def test_overlapping_visits_do_not_create_zero_turnover():
    group=result(expected=5,overlap=True)
    assert group['distributions']['cycle']['median']==10
    assert group['distributions']['change']['n'] is None


def test_complete_day_reference_is_retained():
    group=result(expected=5)
    assert group['distributions']['cycle_complete_days']['median']==10
    assert group['kpi']['free_hours']==8/60


def test_slot_start_inside_does_not_require_end_inside():
    prepared=sample(expected=5)
    frame=prepared['visits']['activity']
    frame['slot_start']=frame.start-pd.Timedelta(minutes=2)
    frame['slot_end']=frame.start+pd.Timedelta(minutes=3)
    frame['booked']=5.
    frame['overlap']=3.
    group=aggregate(prepared,Profile(start='2025-01-02',end='2025-01-02',machines={'M':'Linac'}))['quarter']['activity'][0]['groups'][0]
    assert group['kpi']['duration_ratio_pct']==160
    assert group['kpi']['slot_coverage_pct']==60
    assert group['kpi']['slot_overlap_visits_pct']==100
    assert group['kpi']['fully_in_slot_pct']==0
    assert group['kpi']['slot_position_n']==5


def test_overlap_accepts_early_start_but_not_boundary_touch():
    prepared=sample(expected=5)
    frame=prepared['visits']['activity']
    frame['slot_start']=frame.start+pd.Timedelta(minutes=3)
    frame['slot_end']=frame.start+pd.Timedelta(minutes=13)
    # The last visit ends exactly at slot start, which has zero overlap.
    frame.loc[4,'slot_start']=frame.loc[4,'end']
    group=aggregate(prepared,Profile(start='2025-01-02',end='2025-01-02',machines={'M':'Linac'}))['quarter']['activity'][0]['groups'][0]
    assert group['kpi']['slot_overlap_visits_pct']==80
