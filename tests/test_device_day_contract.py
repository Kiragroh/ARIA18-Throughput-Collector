from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_site_summary_exposes_requested_and_observed_period():
    sql = (ROOT / "sql/datasets/02_site_summary.sql").read_text(encoding="utf-8")
    for field in [
        "requested_period_start",
        "requested_period_end",
        "observed_first_treatment_date",
        "observed_last_treatment_date",
        "selected_machines",
        "active_machines",
        "active_device_days",
    ]:
        assert field in sql

def test_machine_month_exposes_zero_months_and_observed_coverage():
    sql = (ROOT / "sql/datasets/03_machine_month.sql").read_text(encoding="utf-8")
    for field in [
        "period_month",
        "active_machines",
        "active_device_days",
        "first_treatment_date",
        "last_treatment_date",
        "is_active",
    ]:
        assert field in sql
    assert "month_spine" in sql
    assert "CROSS JOIN" in sql


def test_device_day_contains_all_gap_bands_and_time_normalization():
    sql = (ROOT / "sql/datasets/04_device_day.sql").read_text(encoding="utf-8")
    for field in [
        "gap_count_lt15",
        "gap_count_15_29",
        "gap_count_30_59",
        "gap_count_60_119",
        "gap_count_ge120",
        "gap_minutes_ge30",
        "gross_device_hours",
        "net_proxy_hours",
        "sessions_per_10_gross_hours",
        "sessions_per_10_net_proxy_hours",
        "p25_cycle_minutes",
        "p90_cycle_minutes",
    ]:
        assert field in sql
