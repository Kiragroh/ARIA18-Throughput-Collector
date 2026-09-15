import pandas as pd
import pytest
from analysis.contracts import Profile
from analysis.throughput import prepare_visits, aggregate
from analysis.flow import summarize


def slots(n=6):
    return [dict(source="appointment", event_key=str(i), patient_key=str(i),
                 machine="M1", activity_code="TX", status="completed",
                 event_start=f"2025-01-02 08:{i*5:02d}", event_end=f"2025-01-02 08:{i*5+4:02d}",
                 activity_start=f"2025-01-02 08:{i*5:02d}", activity_end=f"2025-01-02 08:{i*5+4:02d}")
            for i in range(n)]


def test_small_device_does_not_hide_publishable_pool():
    rows = slots()
    rows.append(dict(rows[0], machine="M2", patient_key="rare", event_key="rare"))
    profile = Profile(machines={"M1":"Device 1","M2":"Device 2"}, activity_codes={"TX":"treatment_external"})
    groups = aggregate(prepare_visits(pd.DataFrame(rows), profile), profile)["quarter"]["activity"][0]["groups"]
    pool = next(g for g in groups if g["machine"] == "ALL")
    assert pool["kpi"]["visits"] == 6
    assert pool["kpi"]["slot_coverage_pct"] == 100
    assert pool["pool_excludes_suppressed"] is True


def test_duration_ratio_and_calendar_overlap_are_distinct():
    rows = slots()
    for r in rows:
        r["activity_start"] = str(pd.Timestamp(r["event_start"]) + pd.Timedelta(minutes=10))
        r["activity_end"] = str(pd.Timestamp(r["event_end"]) + pd.Timedelta(minutes=10))
    profile = Profile(machines={"M1":"Device 1"}, activity_codes={"TX":"treatment_external"})
    pool = aggregate(prepare_visits(pd.DataFrame(rows), profile),profile)["year"]["activity"][0]["groups"][-1]
    assert pool["kpi"]["slot_coverage_pct"] == 0
    assert pool["kpi"]["duration_ratio_pct"] == 100


def test_resource_fanout_counts_not_clinical_conflicts():
    from analysis.metrics import deduplicate
    a = slots(1)[0]
    frame = pd.DataFrame([dict(a, source_rows=3), dict(a, event_key="copy", source_rows=1)])
    clean, audit = deduplicate(frame)
    assert len(clean) == 1
    assert audit["natural_duplicates"] == 1


def test_multiple_counselling_requires_subsequent_treatment():
    rows = pd.DataFrame([dict(event_key=str(i), patient_key="p", event_start=t, event_end=t,
                              kind="counselling", status="completed")
                         for i,t in enumerate(["2025-01-01","2025-01-12"])])
    result = summarize(rows, Profile(), data_through="2026-06-01", context_start="2024-01-01")
    assert result["counselling_episodes"] == 1
    assert result["multiple_counselling"] == 0


def test_daily_counts_include_manual_modalities_without_double_counting_delivery():
    from analysis.population import treatment_days
    profile=Profile(machines={"M1":"Device 1"}, activity_codes={
        "TX":"treatment_external","TOMO":"treatment_legacy","BR":"treatment_brachy"})
    rows=slots(1)
    rows.extend([
        dict(rows[0], source="delivery", event_key="beam", plan_key="plan", fraction=1, activity_code=""),
        dict(rows[0], event_key="tomo", patient_key="tomo", machine="", activity_code="TOMO"),
        dict(rows[0], event_key="brachy", patient_key="brachy", machine="", activity_code="BR"),
    ])
    days=treatment_days(pd.DataFrame(rows),profile,"2026-04-01")
    assert days.groupby("machine").size().to_dict() == {
        "Device 1":1,"Historische Therapie":1,"Brachytherapie":1}
    assert days.patient_key.nunique() == 3


def test_collector_includes_comparison_population_and_reconciliation_fields():
    from tools.build_collector_v2 import event_sql, FIELDS
    sql=event_sql()
    assert "AppointmentDateTime>=@context AND AppointmentDateTime<DATEADD(day,1,@end)" in sql
    for field in ("activity_name","activity_category","milestone_time","resource_status","patient_class"):
        assert field in FIELDS
