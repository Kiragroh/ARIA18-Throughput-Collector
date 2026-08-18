import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_method_contract_is_explicit_and_portable():
    method = json.loads((ROOT / "method.json").read_text(encoding="utf-8"))
    assert method["method_version"] == "ARIA18-THROUGHPUT-1.1"
    assert method["clinical_start_preference"] == [
        "first_imaging_timestamp", "first_beam_timestamp"
    ]
    assert method["rdl_namespace"] == (
        "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"
    )
    assert method["shared_data_source"] == "/VarianTemplate/Data Sources/variandw"
    assert method["gap_threshold_minutes"] == 30
    assert method["slot_match_min_coverage_pct"] == 50
    assert method["default_minimum_group_patients"] == 5
    assert method["pseudonym_hash"] == "SHA2_256"


def test_session_sql_has_no_site_specific_machine_or_server():
    sql = (ROOT / "sql/fragments/session_base.sql").read_text(encoding="utf-8")
    forbidden = [
        "s050",
        "10.23.",
        "Linac1_",
        "TB1_",
        "HAL1_",
        "medizin.uni-leipzig.de",
    ]
    assert not any(token.casefold() in sql.casefold() for token in forbidden)
    assert "@PeriodStart" in sql
    assert "DATEADD(DAY, 1, @PeriodEnd)" in sql
    assert "ISNULL(fth.IsBrachy, 0) = 0" in sql
    assert "ISNULL(fth.IsImage, 0) = 0" in sql
    assert "COALESCE(NULLIF(am.MachineId" in sql


def test_machine_catalog_is_derived_from_actual_treatment():
    sql = (ROOT / "sql/datasets/01_machine_catalog.sql").read_text(encoding="utf-8")
    assert "FactTreatmentHistory" in sql or "{{SESSION_BASE}}" in sql
    assert "COUNT_BIG" in sql
    assert "first_treatment_date" in sql
    assert "last_treatment_date" in sql
    assert "selected_by_default" in sql
