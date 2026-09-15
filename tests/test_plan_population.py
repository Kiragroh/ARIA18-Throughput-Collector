import pandas as pd
from analysis.contracts import Profile
from analysis.population import treatment_days, plan_courses, summarize_population


def delivery(day, fraction, planned=10, plan="a", machine="M"):
    return dict(source="delivery",event_key=f"{plan}-{day}",patient_key="p",plan_key=plan,
                course_key="c",machine=machine,event_start=day+" 08:00",event_end=day+" 08:10",
                fraction=fraction,planned_fractions=planned,activity_code="",status="delivered")


def plans(rows, through):
    return plan_courses(treatment_days(pd.DataFrame(rows), Profile(machines={"M":"Linac 1"}), through), through)


def test_incomplete_plan_requires_more_than_seven_observed_days():
    rows=[delivery("2025-01-02",1),delivery("2025-01-03",2)]
    assert plans(rows,"2025-01-10").iloc[0].state == "open_followup"
    out=plans(rows,"2025-01-11").iloc[0]
    assert out.state == "ended_incomplete"
    assert out.end.date().isoformat() == "2025-01-03"


def test_completion_is_not_inferred_when_target_missing():
    out=plans([delivery("2025-01-02",1,None)],"2025-02-01").iloc[0]
    assert out.state == "ended_target_unknown"
    assert plans([delivery("2025-01-02",1,1)],"2025-01-03").iloc[0].state == "completed"


def test_resumed_plan_not_counted_as_another_new_plan():
    rows=[delivery("2025-01-02",1),delivery("2025-01-20",2)]
    out=plans(rows,"2025-02-01")
    assert len(out)==1
    assert out.iloc[0].resumed_after_gap
    assert str(out.iloc[0].end.date())=="2025-01-20"


def test_left_truncated_plan_is_not_a_new_start():
    out=plans([delivery("2025-01-02",8)],"2025-02-01").iloc[0]
    assert not out.start_confirmed


def test_machine_change_does_not_duplicate_plan_or_patient():
    rows=[delivery("2025-01-02",1),delivery("2025-01-03",2,machine="Other")]
    assert len(plans(rows,"2025-02-01"))==1


def test_old_export_cannot_claim_previous_year_completeness():
    rows=pd.DataFrame([delivery("2025-01-02",1)])
    profile=Profile(machines={"M":"Linac 1"})
    out=summarize_population(rows,profile,{"data_through":"2026-04-01","context_start":"2024-01-01"})
    assert not out["comparison_available"]
    assert all(p["previous"] is None for p in out["periods"]["quarter"])


def test_unmapped_external_appointment_uses_unique_actual_machine_without_double_counting():
    a=delivery("2025-01-02",1)
    b=dict(a,source="appointment",event_key="slot",machine="",activity_code="TX",status="completed")
    profile=Profile(machines={"M":"Linac 1"},activity_codes={"TX":"treatment_external"})
    days=treatment_days(pd.DataFrame([a,b]),profile,"2025-01-10")
    assert len(days)==1
    assert days.iloc[0].evidence=="technical"


def test_brachy_not_absorbed_by_external_treatment_on_same_day():
    a=delivery("2025-01-02",1)
    b=dict(a,source="appointment",event_key="brachy",machine="",plan_key="",activity_code="BR",status="completed")
    profile=Profile(machines={"M":"Linac 1"},activity_codes={"BR":"treatment_brachy"})
    assert len(treatment_days(pd.DataFrame([a,b]),profile,"2025-01-10"))==2


def test_ambiguous_resource_resolves_only_with_unique_actual_device():
    from analysis.ingest import resolve_treatment_devices
    a=delivery("2025-01-02",1)
    b=dict(a,source="appointment",event_key="slot",machine="AMBIGUOUS_DEVICE",activity_code="TX")
    p=Profile(machines={"M":"Linac 1","M2":"Linac 2"},activity_codes={"TX":"treatment_external"})
    out=resolve_treatment_devices(pd.DataFrame([a,b]),p)
    assert out.iloc[1].machine=="M" and out.iloc[1].machine_inferred
    c=dict(a,machine="M2",event_key="second-device")
    out=resolve_treatment_devices(pd.DataFrame([a,b,c]),p)
    assert out.iloc[1].machine=="AMBIGUOUS_DEVICE"
    assert not out.iloc[1].machine_inferred
