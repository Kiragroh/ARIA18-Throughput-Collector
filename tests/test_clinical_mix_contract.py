from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_capability_inventory_lists_required_sources():
    sql = (ROOT / "sql/datasets/00_capabilities.sql").read_text(encoding="utf-8")
    for source in [
        "FactTreatmentHistory",
        "DimActivityTransaction",
        "vv_ResourceInfo",
        "InSightiveResourceMachine",
    ]:
        assert source in sql
    assert "is_available" in sql


def test_case_mix_uses_aggregate_diagnosis_and_fraction_bands():
    sql = (ROOT / "sql/datasets/06_case_mix.sql").read_text(encoding="utf-8")
    assert "FactCourseDiagnosis" in sql
    assert "LEFT(UPPER(REPLACE" in sql
    for band in [
        "01 Fx",
        "02-05 Fx",
        "06-10 Fx",
        "11-20 Fx",
        ">20 Fx",
        "Fx unbekannt",
    ]:
        assert band in sql
    assert "@MinimumGroupPatients" in sql


def test_imaging_reports_unavailable_instead_of_false_zero():
    sql = (ROOT / "sql/datasets/07_imaging.sql").read_text(encoding="utf-8")
    assert "capability_status" in sql
    assert "nicht verfuegbar" in sql


def test_quality_reports_filter_counts():
    sql = (ROOT / "sql/datasets/08_data_quality.sql").read_text(encoding="utf-8")
    for metric in [
        "raw_rows",
        "excluded_images",
        "excluded_brachy",
        "excluded_test_patients",
        "valid_sessions",
        "missing_machine",
        "missing_fraction",
    ]:
        assert metric in sql
