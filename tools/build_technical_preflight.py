"""Standalone schema/permission report: never selects clinical table rows."""
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from . import build_rdl as layout
    from .build_collector_v2 import NS, capabilities, source_gaps
except ImportError:
    import build_rdl as layout
    from build_collector_v2 import NS, capabilities, source_gaps

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'ARIA18_Technischer_Preflight_1.0.rdl'


def queries():
    return {
        'TechnicalStatus': (
            "SELECT N'1.0' AS preflight_version, N'18' AS tested_aria_major, "
            "N'NOT_DETECTED' AS installed_aria_version, "
            "CONVERT(nvarchar(255),SERVERPROPERTY('ProductVersion')) AS sql_version, "
            "CASE WHEN " + source_gaps() + " THEN N'CHECK_CAPABILITIES' "
            "ELSE N'SCHEMA_ACCESS_OK' END AS result, "
            "N'No clinical rows read; populated timestamps and clinical mappings not tested' AS limitation;",
            ['preflight_version', 'tested_aria_major', 'installed_aria_version', 'sql_version', 'result', 'limitation']),
        'Capabilities': (capabilities(), ['contract_version', 'source_name', 'column_name',
                                        'is_required', 'available', 'schema_available', 'select_allowed']),
        'Scope': (
            "SELECT N'DWH' AS source, N'SCHEMA_AND_PERMISSIONS_ONLY' AS check_scope "
            "UNION ALL SELECT N'VARIAN imaging / waiting area',N'NOT_TESTED_BY_THIS_REPORT' "
            "UNION ALL SELECT N'Activity mapping / timestamp completeness',N'REQUIRES_LOCAL_VALIDATION';",
            ['source', 'check_scope'])}


def create():
    root = ET.parse(ROOT / 'dist/ARIA18_Throughput_Collector_2.0.rdl').getroot()
    uri = NS['r']
    tag = lambda name: '{' + uri + '}' + name
    for name in ('ReportParameters', 'ReportParametersLayout'):
        node = root.find('r:' + name, NS)
        if node is not None:
            root.remove(node)
    sources = root.find('r:DataSources', NS)
    for source in list(sources):
        if source.get('Name') != 'DataSource1':
            sources.remove(source)
    sets = root.find('r:DataSets', NS)
    sets.clear()
    items = root.find('r:ReportSections/r:ReportSection/r:Body/r:ReportItems', NS)
    items.clear()
    top = 0
    for name, (sql, fields) in queries().items():
        ds = ET.SubElement(sets, tag('DataSet'), Name=name)
        query = ET.SubElement(ds, tag('Query'))
        ET.SubElement(query, tag('DataSourceName')).text = 'DataSource1'
        ET.SubElement(query, tag('CommandText')).text = sql
        ET.SubElement(query, tag('Timeout')).text = '60'
        fs = ET.SubElement(ds, tag('Fields'))
        for field in fields:
            node = ET.SubElement(fs, tag('Field'), Name=field)
            ET.SubElement(node, tag('DataField')).text = field
        layout.FIELDS[name] = fields
        layout.PAGE_NAMES[name] = name
        layout.CAPTIONS[name] = name
        table, top = layout._tablix(name, top)
        items.append(ET.fromstring('<root xmlns="' + uri + '">' + table + '</root>')[0])
    root.find('r:ReportSections/r:ReportSection/r:Body/r:Height', NS).text = str(top + 10) + 'mm'
    for prop in root.findall('r:CustomProperties/r:CustomProperty', NS):
        if prop.findtext('r:Name', namespaces=NS) == 'ReportName':
            prop.find('r:Value', NS).text = TARGET[:-4]
    ET.register_namespace('', uri)
    ET.register_namespace('rd', 'http://schemas.microsoft.com/SQLServer/reporting/reportdesigner')
    ET.register_namespace('df', 'http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition/defaultfontfamily')
    target = ROOT / 'dist' / TARGET
    ET.ElementTree(root).write(target, encoding='utf-8', xml_declaration=True)
    return target


if __name__ == '__main__':
    print(create())
