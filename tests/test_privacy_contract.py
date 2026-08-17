from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_detail_exports_use_salted_hashes_and_no_direct_identifiers():
    combined = "\n".join(
        (ROOT / "sql/datasets" / name).read_text(encoding="utf-8")
        for name in ["09_session_details.sql", "10_appointment_details.sql"]
    )
    assert "HASHBYTES('SHA2_256'" in combined
    assert "@ExportSalt" in combined
    forbidden_aliases = [
        " AS PatientId",
        " AS PatientFullName",
        " AS BirthDate",
        " AS DICOMUID",
        " AS FreeText",
    ]
    assert not any(alias.casefold() in combined.casefold() for alias in forbidden_aliases)


def test_session_details_support_reclassification():
    sql = (ROOT / "sql/datasets/09_session_details.sql").read_text(encoding="utf-8")
    for field in [
        "patient_key",
        "course_key",
        "plan_key",
        "session_key",
        "service_date",
        "machine",
        "fraction_number",
        "planned_fractions",
        "technique",
        "diagnosis_group",
        "session_start",
        "session_end",
        "actual_minutes",
        "field_count",
    ]:
        assert field in sql


def test_appointment_details_share_patient_and_session_namespaces():
    sql = (ROOT / "sql/datasets/10_appointment_details.sql").read_text(encoding="utf-8")
    assert ":PAT:" in sql
    assert ":SESSION:" in sql
    assert "appointment_key" in sql
    assert "matched_session_key" in sql
