import re
import xml.etree.ElementTree as ET
from tools.build_technical_preflight import create, queries
from tools.build_collector_v2 import NS
from tools.package_v2 import package_preflight
from zipfile import ZipFile
import hashlib


def test_preflight_has_no_detail_datasets_parameters_or_row_reads():
    root = ET.parse(create()).getroot()
    assert {x.get('Name') for x in root.findall('r:DataSets/r:DataSet', NS)} == set(queries())
    assert root.find('r:ReportParameters', NS) is None
    for node in root.findall('.//r:CommandText', NS):
        sql = node.text
        # Only constant VALUES projections are allowed as a FROM source.
        assert not re.search(r'\b(?:JOIN|EXEC|INSERT|UPDATE|DELETE|DROP|INTO)\b', sql, re.I)
        assert all(re.match(r'\s*\(VALUES\b', sql[m.end():], re.I)
                   for m in re.finditer(r'\bFROM\b', sql, re.I))
        assert 'HASHBYTES' not in sql
    fields = {x.get('Name') for x in root.findall('.//r:Field', NS)}
    assert not fields.intersection({'patient_key', 'event_key', 'plan_key', 'course_key', 'event_start', 'event_end'})
    assert 'NOT_TESTED_BY_THIS_REPORT' in ET.tostring(root, encoding='unicode')


def test_preflight_bundle_contains_only_schema_report_and_instructions():
    create()
    with ZipFile(package_preflight()) as archive:
        assert set(archive.namelist()) == {'README.md', 'ARIA18_Technischer_Preflight_1.0.rdl', 'SHA256SUMS.txt'}
        for line in archive.read('SHA256SUMS.txt').decode().splitlines():
            digest, name = line.split('  ', 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
