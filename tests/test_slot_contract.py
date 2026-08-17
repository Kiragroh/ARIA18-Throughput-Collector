from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_resource_sql_supports_both_aria18_resource_paths():
    sql = (ROOT / "sql/fragments/resource_base.sql").read_text(encoding="utf-8")
    assert "vv_ResourceInfo" in sql
    assert "InSightiveResourceMachine" in sql
    assert "OBJECT_ID" in sql
    assert "mapping_source" in sql


def test_slot_matching_is_deduplicated_and_one_to_one():
    sql = (ROOT / "sql/datasets/05_slot_summary.sql").read_text(encoding="utf-8")
    assert "duplicate_rank" in sql
    assert "appointment_rank" in sql
    assert "session_rank" in sql
    assert "appointment_rank = 1 AND session_rank = 1" in sql
    assert "match_coverage_pct" in sql
    assert "avg_slot_utilization_pct" in sql
    assert "@MinimumGroupPatients" in sql
