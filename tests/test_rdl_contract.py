from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RDL = ROOT / "dist/ARIA18_Durchsatz_Klinikvergleich_Collector.rdl"
NS = "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def test_generated_rdl_contract():
    root = ET.parse(RDL).getroot()
    assert root.tag.startswith(f"{{{NS}}}")
    parameters = {
        node.attrib["Name"]
        for node in root.iter()
        if local(node.tag) == "ReportParameter"
    }
    assert {
        "SiteLabel",
        "PeriodStart",
        "PeriodEnd",
        "Machines",
        "MachineList",
        "MinimumGroupPatients",
        "IncludePseudonymizedDetails",
        "MethodVersion",
        "RunId",
        "ExportSalt",
    } <= parameters
    datasets = {
        node.attrib["Name"] for node in root.iter() if local(node.tag) == "DataSet"
    }
    assert {
        "Capabilities",
        "MachineCatalog",
        "SiteSummary",
        "MachineMonth",
        "DeviceDay",
        "SlotSummary",
        "CaseMix",
        "Imaging",
        "DataQuality",
        "Glossary",
        "SessionDetails",
        "AppointmentDetails",
    } <= datasets
    text = RDL.read_text(encoding="utf-8")
    assert "{{" not in text
    assert "/VarianTemplate/Data Sources/variandw" in text


def test_export_page_names_are_stable():
    root = ET.parse(RDL).getroot()
    page_names = {
        node.text for node in root.iter() if local(node.tag) == "PageName" and node.text
    }
    required = {
        "00_Coverage",
        "01_SiteSummary",
        "02_MachineMonth",
        "03_DeviceDay",
        "04_SlotSummary",
        "05_CaseMix",
        "06_Imaging",
        "07_DataQuality",
        "08_Glossary",
        "90_Sessions",
        "91_Appointments",
    }
    assert all(any(marker in page_name for page_name in page_names) for marker in required)


def test_generated_rdl_has_no_fixed_site_or_direct_output_identifier():
    text = RDL.read_text(encoding="utf-8")
    forbidden = [
        "medizin.uni-leipzig.de",
        "10.23.",
        "s050",
        "Linac1_",
        "TB1_",
        "HAL1_",
        "PatientFullName",
        "PatientDateOfBirth",
    ]
    assert not any(token.casefold() in text.casefold() for token in forbidden)
    assert '<Field Name="PatientId">' not in text
    assert '<Field Name="DimPatientID">' not in text
