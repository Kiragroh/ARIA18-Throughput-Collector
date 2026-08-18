from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RDL = ROOT / "dist/ARIA18_Durchsatz_Klinikvergleich_Collector.rdl"
NAMESPACE = "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"
REQUIRED_PARAMETERS = {
    "SiteLabel", "PeriodStart", "PeriodEnd", "Machines", "MachineList",
    "MinimumGroupPatients", "IncludePseudonymizedDetails", "MethodVersion",
    "RunId", "ExportSalt",
}
REQUIRED_DATASETS = {
    "Capabilities", "MachineCatalog", "SiteSummary", "MachineMonth",
    "DeviceDay", "SlotSummary", "CaseMix", "Imaging", "DataQuality",
    "Glossary", "SessionDetails", "AppointmentDetails",
}
REQUIRED_PAGE_MARKERS = {
    "00_Coverage", "01_SiteSummary", "02_MachineMonth", "03_DeviceDay",
    "04_SlotSummary", "05_CaseMix", "06_Imaging", "07_DataQuality",
    "08_Glossary", "90_Sessions", "91_Appointments",
}
FORBIDDEN = {
    "medizin.uni-leipzig.de", "10.23.", "s050", "Linac1_", "TB1_",
    "HAL1_", "PatientFullName", "PatientDateOfBirth",
}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate(path: Path = RDL) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"RDL fehlt: {path}"]
    text = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [f"XML ungueltig: {exc}"]
    if root.tag != f"{{{NAMESPACE}}}Report":
        errors.append("Falscher RDL-2016-Namespace")
    parameters = {
        node.attrib.get("Name", "") for node in root.iter()
        if local(node.tag) == "ReportParameter"
    }
    datasets = {
        node.attrib.get("Name", "") for node in root.iter()
        if local(node.tag) == "DataSet"
    }
    page_names = {
        (node.text or "") for node in root.iter() if local(node.tag) == "PageName"
    }
    missing_parameters = REQUIRED_PARAMETERS - parameters
    missing_datasets = REQUIRED_DATASETS - datasets
    missing_pages = {
        marker for marker in REQUIRED_PAGE_MARKERS
        if not any(marker in page_name for page_name in page_names)
    }
    if missing_parameters:
        errors.append(f"Parameter fehlen: {sorted(missing_parameters)}")
    if missing_datasets:
        errors.append(f"Datasets fehlen: {sorted(missing_datasets)}")
    if missing_pages:
        errors.append(f"Exportseiten fehlen: {sorted(missing_pages)}")
    if "/VarianTemplate/Data Sources/variandw" not in text:
        errors.append("Gemeinsame variandw-Datenquelle fehlt")
    if "{{" in text:
        errors.append("Nicht aufgeloeste Template-Tokens")
    fixed = sorted(token for token in FORBIDDEN if token.casefold() in text.casefold())
    if fixed:
        errors.append(f"Feste Standort- oder Identifikator-Tokens: {fixed}")
    direct_fields = ["PatientId", "DimPatientID", "PatientFullName", "BirthDate"]
    for field in direct_fields:
        if f'<Field Name="{field}">' in text:
            errors.append(f"Direktes Identifikatorfeld im RDL: {field}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"RDL_VALIDATION_ERROR: {error}")
        return 1
    print("RDL_VALIDATION_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
