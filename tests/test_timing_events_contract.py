from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_appointment_export_contains_workflow_timestamps():
    resource_sql = (ROOT / "sql/fragments/resource_base.sql").read_text(encoding="utf-8")
    detail_sql = (ROOT / "sql/datasets/10_appointment_details.sql").read_text(encoding="utf-8")

    for token in (
        "patient_arrival_timestamp",
        "pending_or_in_progress_timestamp",
        "completed_timestamp",
        "PatientArrivalDateTime",
        "ScheduledActivityHstryDateTime",
        "IN PROGRESS",
        "PENDING",
        "MANUALLY COMPLETED",
    ):
        assert token in resource_sql

    for token in (
        "arrival_to_clinical_start_minutes",
        "arrival_timing_quality",
        "slot_to_clinical_start_minutes",
        "pending_to_clinical_start_minutes",
        "matched_first_imaging_timestamp",
        "matched_first_beam_timestamp",
        "matched_clinical_start_timestamp",
    ):
        assert token in detail_sql


def test_session_export_keeps_imaging_and_beam_separate():
    session_sql = (ROOT / "sql/fragments/session_base.sql").read_text(encoding="utf-8")
    detail_sql = (ROOT / "sql/datasets/09_session_details.sql").read_text(encoding="utf-8")

    assert "raw_imaging" in session_sql
    assert "first_imaging_timestamp" in session_sql
    assert "first_beam_timestamp" in session_sql
    assert "i.first_imaging_timestamp <= s.first_beam_timestamp" in session_sql
    assert "imaging_after_beam_flag" in detail_sql


def test_glossary_is_an_exported_dataset():
    builder = (ROOT / "tools/build_rdl.py").read_text(encoding="utf-8")
    glossary = ROOT / "sql/datasets/11_glossary.sql"

    assert glossary.exists()
    assert '"Glossary": "11_glossary.sql"' in builder
    assert '"Glossary": "08_Glossary"' in builder
