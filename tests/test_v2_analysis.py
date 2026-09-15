from pathlib import Path
import json
import pandas as pd
import pytest


def modules():
    import importlib.util
    assert importlib.util.find_spec("analysis") is not None, "2.0 analysis package missing"
    from analysis import contracts, metrics, flow
    return contracts, metrics, flow


def test_default_year_and_reason():
    c, _, _ = modules()
    p = c.Profile()
    assert (p.start, p.end, p.model) == ("2025-01-01", "2025-12-31", "activity")
    alternative = c.Profile(start="2024-01-01", end="2024-12-31")
    assert alternative.period_reason == ""


def test_interval_union_nested_overlap_and_threshold():
    _, m, _ = modules()
    stats = m.interval_stats([(0, 60), (20, 30), (90, 100), (131, 150)])
    assert stats["occupied_minutes"] == 89
    assert stats["free_minutes"] == 61
    assert stats["free_gt30_minutes"] == 31
    assert stats["gap_eq30_count"] == 1
    assert stats["window_minutes"] == 150
    assert stats["overlap_minutes"] == 10


def test_conflicting_duplicates_are_not_arbitrarily_selected():
    _, m, _ = modules()
    frame = pd.DataFrame([{"event_key":"x","patient_key":"p","status":"Completed"},
                          {"event_key":"x","patient_key":"p","status":"Cancelled"},
                          {"event_key":None,"patient_key":"a","status":"Completed"},
                          {"event_key":None,"patient_key":"b","status":"Completed"}])
    clean, audit = m.deduplicate(frame)
    assert len(clean) == 2
    assert audit["conflicting_keys"] == 1
    assert audit["missing_keys"] == 2


def event(key, person, when, kind, status="completed", end=None):
    return dict(event_key=key, patient_key=person, event_start=when,
                event_end=end or when, kind=kind, status=status)


def test_flow_manual_therapy_repeats_and_not_window_end():
    c, _, f = modules()
    events = pd.DataFrame([
        event("a","p","2025-01-01","counselling"),
        event("b","p","2025-01-10","counselling"),
        event("c","p","2025-01-20","treatment_brachy",end="2025-02-01"),
        event("d","q","2025-06-01","counselling"),
        event("e","q","2025-12-01","observation","open"),
        event("f","r","2025-07-01","counselling"),
        event("g","s","2025-12-15","counselling"),
    ])
    out = f.summarize(events, c.Profile(), data_through="2026-01-01",
                      context_start="2024-01-01", sources_complete=True)
    assert out["completed_counselling_appointments"] == 5
    assert out["counselling_episodes"] == 4
    assert out["mature_episodes"] == 3
    assert out["matched_mature"] == 1
    assert out["observation_mature"] == 1
    assert out["unresolved_mature"] == 1
    assert out["provisional"] == 1
    assert out["multiple_counselling"] == 1
    assert out["treatment_episodes"] == 1
    assert out["unresolved_pct"] == pytest.approx(100/3)


def test_three_calendar_months_not_90_days_and_missing_coverage():
    c, _, f = modules()
    events = pd.DataFrame([event("a","p","2025-01-31","counselling")])
    early = f.summarize(events, c.Profile(), data_through="2025-04-29",
                        context_start="2024-01-01", sources_complete=True)
    assert early["mature_episodes"] == 0
    unknown = f.summarize(events, c.Profile(), data_through="2025-05-01",
                          context_start="2024-01-01", sources_complete=False)
    assert unknown["unresolved_pct"] is None


def test_slot_coverage_is_overlap_not_actual_duration():
    _, m, _ = modules()
    assert m.slot_overlap(0,20,10,40) == 10
    assert m.slot_overlap(0,20,30,40) == 0


def test_report_suppression_removes_small_group_values():
    c, m, _ = modules()
    q = m.distribution([1,2,3], {"p1","p2","p3"}, 5)
    assert q["suppressed"] is True
    assert q["median"] is None
    assert "values" not in q


def test_models_change_intervals_and_unmatched_appointments_survive():
    modules()
    from analysis.throughput import prepare_visits
    from analysis.contracts import Profile
    rows = [
        dict(event_key="beam",patient_key="p",source="delivery",machine="M1",
             event_start="2025-01-02 08:05",event_end="2025-01-02 08:10",plan_key="plan",
             course_key="course",fraction=1,activity_code="",status="delivered"),
        dict(event_key="image",patient_key="p",source="imaging",machine="M1",
             event_start="2025-01-02 08:03",event_end="2025-01-02 08:04",plan_key="plan",
             course_key="course",fraction=1,activity_code="",status="completed"),
        dict(event_key="appointment",patient_key="p",source="appointment",machine="M1",
             event_start="2025-01-02 08:00",event_end="2025-01-02 08:20",
             activity_start="2025-01-02 08:01",activity_end="2025-01-02 08:15",
             completed="2025-01-02 08:16",activity_code="TX",status="completed"),
        dict(event_key="unmatched",patient_key="q",source="appointment",machine="M1",
             event_start="2025-01-02 08:20",event_end="2025-01-02 08:40",
             activity_code="TX",status="open"),
    ]
    p = Profile(confirmed=True, machines={"M1":"Machine 1"},activity_codes={"TX":"treatment_external"})
    result = prepare_visits(pd.DataFrame(rows),p)
    assert result["audit"]["relevant_slots"] == 2
    assert result["audit"]["matched_slots"] == 1
    assert result["visits"]["activity"].iloc[0].duration == 14
    assert result["visits"]["workflow"].iloc[0].duration == 13
    assert result["visits"]["technical"].iloc[0].duration == 7


def test_cache_uses_content_and_profile(tmp_path):
    modules()
    from analysis.cache import cache_key
    from analysis.contracts import Profile
    source = tmp_path/"same.xlsx"
    source.write_bytes(b"first")
    a = cache_key(source, Profile())
    source.write_bytes(b"second")
    assert cache_key(source, Profile()) != a
    assert cache_key(source, Profile(model="workflow")) != cache_key(source, Profile())


def test_report_only_receives_aggregate_allowlist(tmp_path):
    modules()
    from analysis.report import render
    data = dict(version="2.0",site="Test",start="2025-01-01",end="2025-12-31",
                periods={},flow={},quality={},notes=[],patient_key="SECRET_PERSON")
    with pytest.raises(ValueError,match="aggregate"):
        render(data,tmp_path/"report.html")


def test_resource_fanout_same_appointment_is_one_even_with_different_source_keys():
    _,m,_=modules()
    rows=pd.DataFrame([
        dict(event_key="a",source="appointment",patient_key="p",activity_code="CONS",
             event_start="2025-01-01 08:00",machine="",status="completed"),
        dict(event_key="b",source="appointment",patient_key="p",activity_code="CONS",
             event_start="2025-01-01 08:00",machine="",status="completed")])
    clean,audit=m.deduplicate(rows)
    assert len(clean)==1
    assert audit["natural_duplicates"]==1


def test_mixed_iso_precision_preserves_measured_activity_and_flow():
    from analysis.throughput import prepare_visits
    from analysis.contracts import Profile
    from analysis.flow import summarize
    rows=pd.DataFrame([
        dict(event_key=str(i),source="appointment",patient_key=str(i),machine="M1",
             activity_code="TX",status="completed",event_start=t,
             event_end=e,activity_start=t,activity_end=e,kind="treatment_external")
        for i,(t,e) in enumerate([
            ("2025-01-02T08:00:00","2025-01-02T08:15:00"),
            ("2025-01-02T08:20:00.123","2025-01-02T08:35:00.123")])])
    profile=Profile(machines={"M1":"Machine 1"},activity_codes={"TX":"treatment_external"})
    prepared=prepare_visits(rows,profile)
    assert len(prepared["visits"]["activity"])==2
    assert prepared["visits"]["activity"].duration.tolist()==[15,15]
    flow=summarize(rows,profile,data_through="2026-04-01",context_start="2024-01-01")
    assert flow["treatment_episodes"]==2


def test_suppression_propagates_through_overlapping_totals():
    from analysis.cli import suppress_flow
    result=suppress_flow(dict(multiple_counselling=1,counselling_episodes=90,
        completed_counselling_appointments=100,registered_counselling_appointments=120,
        open_counselling_appointments=10,cancelled_counselling_appointments=10),5)
    assert result["registered_counselling_appointments"] is None
