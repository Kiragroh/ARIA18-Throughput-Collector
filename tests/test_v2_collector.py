from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"r":"http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}


def test_v2_rdl_contract_and_default_year():
    path = ROOT / "dist/ARIA18_Throughput_Collector_2.0.rdl"
    assert path.exists(), "2.0 collector missing"
    root = ET.parse(path).getroot()
    parameters = {p.get("Name"):p for p in root.findall("r:ReportParameters/r:ReportParameter", NS)}
    assert "2025" in parameters["PeriodStart"].findtext("r:DefaultValue/r:Values/r:Value", namespaces=NS)
    assert "2025" in parameters["PeriodEnd"].findtext("r:DefaultValue/r:Values/r:Value", namespaces=NS)
    assert {"DataThrough","ContextStart","PeriodReason"} <= parameters.keys()
    assert set(d.get("Name") for d in root.findall("r:DataSets/r:DataSet",NS)) == {
        "Metadata","Capabilities","ActivityCatalog","EventDetails","AppointmentInventory",
        "MachineInventory","HistoryStatusInventory","CompletionDiagnostics","VersionInfo"}
    assert root.find(".//r:Query/r:Timeout",NS) is not None


def test_visible_parameters_are_simple_and_analysis_details_are_enabled():
    for name in ['ARIA18_Throughput_Collector_2.0.rdl','ARIA18_Throughput_Collector_Fast_2.0.rdl']:
        root=ET.parse(ROOT/'dist'/name).getroot()
        params={p.get('Name'):p for p in root.findall('r:ReportParameters/r:ReportParameter',NS)}
        assert {n for n,p in params.items() if p.findtext('r:Hidden',namespaces=NS)!='true'} == {
            'SiteLabel','PeriodStart','PeriodEnd'}
        assert params['IncludePseudonymizedDetails'].findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)=='true'
        assert params['SiteLabel'].findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)=='\u00c4ndere mich'
        assert params['DataThroughConfirmed'].findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)=='false'
        assert 'DateAdd' in params['ContextStart'].findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)
        assert 'Today()' in params['DataThrough'].findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)
    preflight=ET.parse(ROOT/'dist/ARIA18_Standort_Preflight_2.0.rdl')
    param=preflight.find("r:ReportParameters/r:ReportParameter[@Name='IncludePseudonymizedDetails']",NS)
    assert param.findtext('r:DefaultValue/r:Values/r:Value',namespaces=NS)=='false'


def test_full_activity_catalog_does_not_use_the_cohort_window():
    from tools.build_collector_v2 import stage
    assert ' WHERE ' not in stage('Activity')


def test_sql_has_no_direct_identifiers_or_silent_schema_failures():
    path = ROOT / "dist/ARIA18_Throughput_Collector_2.0.rdl"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "sp_executesql" in text and "THROW" in text
    assert "IsMOTestPatient" in text
    for forbidden in ("PatientFullName","ResourceFullName","PatientDateOfBirth","NOLOCK"):
        assert forbidden not in text
    # PatientId/last name may only classify source rows inside the query, never be exported.
    root = ET.fromstring(text)
    for field in root.findall(".//r:Fields/r:Field",NS):
        assert field.get("Name") not in {"PatientId","PatientLastName","DimPatientID"}
    from tools.build_collector_v2 import event_sql
    final = event_sql().rsplit("\nSELECT N'2.0' AS contract_version",1)[1]
    assert "PatientId" not in final and "PatientLastName" not in final
    assert "2025" in text


def test_source_query_compacts_records_and_resolves_resource_fanout():
    from tools.build_collector_v2 import event_sql
    sql=event_sql()
    assert "appointment_devices" in sql
    assert "grouped_events" in sql
    assert "source_rows" in sql
    assert "a.AppointmentResourceStatus LIKE" not in sql


def test_context_is_limited_to_actual_period_cohort_before_loading_history():
    from tools.build_collector_v2 import event_sql
    sql=event_sql()
    assert "#Cohort" in sql
    assert sql.index("CREATE INDEX ix_appointment_id")<sql.index("INSERT INTO #History")


def test_preflight_has_no_patient_detail_dataset_and_valid_table_links():
    path=ROOT/'dist/ARIA18_Standort_Preflight_2.0.rdl'
    root=ET.parse(path).getroot()
    sets={s.get('Name'):s for s in root.findall('r:DataSets/r:DataSet',NS)}
    assert 'EventDetails' not in sets
    assert {'AppointmentInventory','MachineInventory','HistoryStatusInventory'}<=set(sets)
    for table in root.findall('.//r:Tablix',NS):
        assert table.findtext('r:DataSetName',namespaces=NS) in sets
    for source in sets.values():
        for field in source.findall('r:Fields/r:Field',NS):
            assert field.get('Name') not in {'patient_key','event_key','course_key','plan_key','DimPatientID'}
