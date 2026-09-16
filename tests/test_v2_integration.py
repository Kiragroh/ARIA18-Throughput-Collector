from pathlib import Path
import json
import pandas as pd
import pytest
from analysis.contracts import Profile
from analysis.ingest import load_export
from analysis.metrics import deduplicate,distribution
from analysis.flow import summarize


def test_repeated_observation_after_cancellation_and_new_course():
    rows=[]
    for key,time,kind,status in [
        ("1","2025-01-01","counselling","completed"),
        ("2","2025-02-01","treatment_external","completed"),
        ("3","2025-06-01","counselling","completed"),
        ("4","2025-07-01","observation","cancelled"),
        ("5","2025-09-01","observation","completed"),
        ("6","2025-12-01","observation","open")]:
        rows.append(dict(event_key=key,patient_key="p",event_start=time,event_end=time,kind=kind,status=status))
    result=summarize(pd.DataFrame(rows),Profile(),data_through="2026-01-01",
                     context_start="2024-01-01",sources_complete=True)
    assert result["counselling_episodes"]==2
    assert result["matched_mature"]==1
    assert result["observation_mature"]==1
    assert result["unresolved_mature"]==0


def test_new_therapy_30_days_merges_but_31_does_not():
    rows=[dict(event_key=str(i),patient_key="p",kind="treatment_brachy",status="completed",
               event_start=t,event_end=t) for i,t in enumerate(["2025-01-01","2025-01-31","2025-03-03"])]
    result=summarize(pd.DataFrame(rows),Profile(),data_through="2025-12-31",
                     context_start="2024-01-01",sources_complete=True)
    assert result["treatment_episodes"]==2


def test_window_end_is_not_assumed_treatment_end():
    row=dict(event_key="x",patient_key="p",kind="treatment_external",status="completed",
             event_start="2025-12-20",event_end="2025-12-30")
    result=summarize(pd.DataFrame([row]),Profile(),data_through="2025-12-31",
                     context_start="2024-01-01",sources_complete=True)
    assert result["completed_treatment_episodes"]==0


def test_strict_patient_threshold_and_no_samples_returned():
    result=distribution([1,2,100,200,300],{"same-person"},5)
    assert result["suppressed"] and all(result[k] is None for k in ["q1","median","q3","low","high"])


def test_missing_export_contract_is_rejected(tmp_path):
    from openpyxl import Workbook
    path=tmp_path/"bad.xlsx"
    wb=Workbook();wb.active.append(["patient_key","secret"]);wb.save(path)
    with pytest.raises(ValueError,match="Unsupported export"):
        load_export(path)


def test_flat_csv_export_preserves_metadata_and_iso_time(tmp_path):
    path=tmp_path/"export.csv"
    pd.DataFrame([dict(contract_version="2.0",run_id="test",period_start="2025-01-01",
                      period_end="2025-12-31",context_start="2024-01-01",data_through="2026-04-01",
                      data_through_confirmed=0,source="appointment",event_key="e",
                      patient_key="p",event_start="2025-01-15T08:00:00",event_end="2025-01-15T08:30:00",
                      machine="M1",activity_code="CONS",status="completed")]).to_csv(path,index=False)
    meta,events,_,_=load_export(path)
    assert meta["period_start"]=="2025-01-01"
    assert len(events)==1


def test_watermark_can_be_confirmed_locally_without_rdl_checkbox():
    from analysis.cli import watermark_confirmed
    metadata={'data_through':'2026-04-01','data_through_confirmed':False}
    assert not watermark_confirmed(metadata,Profile())
    assert not watermark_confirmed(metadata,Profile(complete_through='2026-03-31'))
    assert watermark_confirmed(metadata,Profile(complete_through='2026-04-01'))
    assert not watermark_confirmed(dict(metadata,data_through='2026-05-01'),Profile(complete_through='2026-04-01'))
    assert watermark_confirmed(dict(metadata,data_through_confirmed=True),Profile())


def test_future_watermark_is_not_a_local_confirmation():
    from datetime import date
    with pytest.raises(ValueError,match='complete past date'):
        Profile(complete_through=date.today().isoformat())


def test_small_auxiliary_flow_cell_does_not_erase_unrelated_totals():
    from analysis import cli
    assert hasattr(cli,"suppress_flow")
    result=cli.suppress_flow(dict(completed_counselling_appointments=100,counselling_episodes=90,
                                 treatment_episodes=80,open_with_treatment=1),5)
    assert result["completed_counselling_appointments"]==100
    assert result["open_with_treatment"] is None


def test_missing_middle_interval_is_not_free_time(connected_rows):
    from analysis.throughput import prepare_visits,aggregate
    rows=[]
    for i in range(6):
        start=pd.Timestamp('2025-01-02 08:00')+pd.Timedelta(minutes=20*i)
        rows.append(dict(event_key=str(i),patient_key=str(i),source='appointment',
            machine='M1',activity_code='TX',status='completed',event_start=start,
            event_end=start+pd.Timedelta(minutes=20),activity_start=start if i!=2 else None,
            activity_end=start+pd.Timedelta(minutes=15) if i!=2 else None))
    profile=Profile(machines={'M1':'Machine 1'},activity_codes={'TX':'treatment_external'})
    rows = connected_rows(rows)
    prepared=prepare_visits(pd.DataFrame(rows),profile)
    group=aggregate(prepared,profile)['year']['activity'][0]['groups'][0]
    assert group['kpi']['visits']==5
    assert group['kpi']['free_hours'] is None
    assert group['distributions']['free']['median'] is None
    assert group['kpi']['incomplete_device_days']==1
