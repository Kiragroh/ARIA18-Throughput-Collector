import xml.etree.ElementTree as ET
from tools import build_collector_v2 as builder
from analysis.contracts import Profile

NS = {"r": "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}


def test_no_required_reason_or_site_entry():
    root = ET.parse(builder.build())
    for name in ("PeriodReason", "SiteLabel"):
        param = root.find(f"r:ReportParameters/r:ReportParameter[@Name='{name}']", NS)
        assert param.findtext("r:AllowBlank", namespaces=NS) == "true"
    Profile(start="2025-01-01", end="2025-02-28")


def test_repeated_completion_does_not_discard_the_first_end():
    text = builder.build().read_text(encoding="utf-8")
    assert "MIN(h.ScheduledActivityHstryDateTime)" in text
    assert "CASE WHEN h.candidate_count=1 THEN h.completed END" not in text
    assert "N'PT. COMPLTFINISH'" in text
    assert "h.candidate_count" in text


def test_combined_report_has_diagnostics_and_graceful_source_guard():
    root = ET.parse(builder.build())
    datasets = {ds.attrib["Name"]: ds.findtext("r:Query/r:CommandText", namespaces=NS)
                for ds in root.findall("r:DataSets/r:DataSet", NS)}
    assert {"VersionInfo", "CompletionDiagnostics", "AppointmentInventory",
            "MachineInventory", "HistoryStatusInventory", "EventDetails"} <= datasets.keys()
    assert "NOT_DETECTED" in datasets["VersionInfo"]
    assert "SQL-Version, nicht ARIA-Version" in datasets["VersionInfo"]
    assert "EVENTS_UNAVAILABLE_CHECK_CAPABILITIES" in datasets["Metadata"]
    assert "delivery_evidence_any_of_MU_or_dose" in datasets["Capabilities"]
    events = datasets["EventDetails"]
    assert events.index("COL_LENGTH") < events.index("#Cohort")
    assert "RETURN;" in events
