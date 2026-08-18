from pathlib import Path
import sys

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_single_site
from analyze_single_site import load_ssrs_sheet, summarize_waiting_times


def _workbook_with_sheet(path: Path, title: str, headers: list[str], rows: list[list]):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append([None, "Test report"])
    ws.append([])
    ws.append([None, "Caption"])
    ws.append([None, *headers])
    for row in rows:
        ws.append([None, *row])
    wb.save(path)


def test_load_ssrs_sheet_finds_header_row(tmp_path):
    source = tmp_path / "collector.xlsx"
    _workbook_with_sheet(source, "01_SiteSummary", ["SiteLabel", "delivered_sessions"], [["Leipzig", 42]])

    frame = load_ssrs_sheet(source, "01_SiteSummary")

    assert frame.to_dict("records") == [{"SiteLabel": "Leipzig", "delivered_sessions": 42}]


def test_waiting_summary_uses_clinical_start_proxy(tmp_path):
    source = tmp_path / "collector.xlsx"
    _workbook_with_sheet(
        source,
        "91_Appointments_2026",
        ["machine", "arrival_to_clinical_start_minutes", "slot_to_clinical_start_minutes"],
        [["TB1", 12.0, 3.0], ["TB1", 18.0, 5.0], ["TB2", None, -2.0]],
    )

    summary = summarize_waiting_times(source)

    tb1 = summary.loc[summary["machine"] == "TB1"].iloc[0]
    assert tb1["arrival_samples"] == 2
    assert tb1["median_arrival_to_clinical_start_minutes"] == 15.0


def test_waiting_summary_reports_loading_and_completion_intervals(tmp_path):
    source = tmp_path / "collector.xlsx"
    _workbook_with_sheet(
        source,
        "91_Appointments",
        [
            "machine",
            "arrival_to_pending_minutes",
            "pending_to_clinical_start_minutes",
            "clinical_start_to_completed_minutes",
        ],
        [["TB1", 8.0, 4.0, 15.0], ["TB1", 12.0, 6.0, 19.0]],
    )

    row = summarize_waiting_times(source).iloc[0]
    assert row["arrival_to_pending_samples"] == 2
    assert row["median_arrival_to_pending_minutes"] == 10.0
    assert row["pending_samples"] == 2
    assert row["median_pending_to_clinical_start_minutes"] == 5.0
    assert row["completed_samples"] == 2
    assert row["median_clinical_start_to_completed_minutes"] == 17.0


def test_session_timing_summary_reports_imaging_coverage(tmp_path):
    source = tmp_path / "collector.xlsx"
    _workbook_with_sheet(
        source,
        "90_Sessions_2026",
        ["machine", "first_imaging_timestamp", "first_beam_timestamp", "imaging_to_beam_minutes", "imaging_after_beam_flag"],
        [["TB1", "2026-01-01 08:00", "2026-01-01 08:02", 2.0, 0], ["TB1", None, "2026-01-01 08:20", None, 0]],
    )

    assert hasattr(analyze_single_site, "summarize_session_timing")
    summary = analyze_single_site.summarize_session_timing(source)
    assert summary.loc[0, "sessions"] == 2
    assert summary.loc[0, "imaging_sessions"] == 1
    assert summary.loc[0, "imaging_coverage_pct"] == 50.0
