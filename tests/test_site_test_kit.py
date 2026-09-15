import hashlib
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET
import zipfile

from tools.build_site_test_kit import build, FILES

ROOT = Path(__file__).resolve().parents[1]
NS = {'r': 'http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition'}


def test_execution_kit_has_only_documented_files_with_verified_hashes():
    with zipfile.ZipFile(build()) as archive:
        assert len(archive.namelist()) == len(FILES) + 1
        assert set(archive.namelist()) == set(FILES) | {'SHA256SUMS.txt'}
        for line in archive.read('SHA256SUMS.txt').decode('ascii').splitlines():
            digest, name = line.split('  ', 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        for name, source in FILES.items():
            assert archive.read(name) == (ROOT / source).read_bytes()


def test_kit_build_is_repeatable():
    first = build().read_bytes()
    assert build().read_bytes() == first


def test_documented_url_sets_only_editable_parameters_with_details_by_default():
    text = (ROOT / 'kooperation/RDL_AUSFUEHREN.md').read_text(encoding='utf-8')
    urls = re.findall(r'^https://REPORTSERVER[^\s]+', text, re.MULTILINE)
    assert len(urls) == 1
    for url in urls:
        parts = urlsplit(url)
        assert parts.hostname == 'reportserver.example.invalid'
        catalog, query = parts.query.split('&', 1)
        rdl = ET.parse(ROOT / 'dist' / (catalog.rsplit('/', 1)[-1] + '.rdl'))
        known = {p.attrib['Name'] for p in rdl.findall('r:ReportParameters/r:ReportParameter', NS)
                 if p.findtext('r:Hidden', namespaces=NS) != 'true'}
        parameters = parse_qs(query)
        assert set(parameters) <= known | {'rs:Command', 'rs:Format'}
        assert 'IncludePseudonymizedDetails' not in parameters
        assert 'DataThroughConfirmed' not in parameters
        assert parameters['rs:Format'] == ['EXCELOPENXML']
        assert parameters['PeriodStart'] == ['2025-01-01']
        default = rdl.find("r:ReportParameters/r:ReportParameter[@Name='IncludePseudonymizedDetails']/r:DefaultValue/r:Values/r:Value", NS)
        assert default.text == 'true'


def test_first_test_form_is_offline_and_not_an_analysis_profile():
    html = (ROOT / 'kooperation/START_HIER.html').read_text(encoding='utf-8')
    assert "connect-src 'none'" in html and "form-action 'none'" in html
    assert 'fetch(' not in html and 'XMLHttpRequest' not in html and 'localStorage' not in html
    assert "schema_version:'cooperation-2'" in html
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://', html)
    assert 'IncludePseudonymizedDetails:' not in html
    assert 'id="reportKind"' not in html and 'id="reviewed"' not in html
    assert 'id="textDownload"' not in html and 'id="printForm"' not in html
    assert "'text/plain'" not in html and "window.print" not in html
    assert 'JSON herunterladen' in html and 'JSON und die Exceldatei' in html
    assert "['identityFields','email'" in html and "['identityFields','replaces'" in html


def test_preflight_contains_no_event_dataset():
    root = ET.parse(ROOT / 'dist/ARIA18_Standort_Preflight_2.0.rdl')
    assert all(d.attrib['Name'] != 'EventDetails' for d in root.findall('r:DataSets/r:DataSet', NS))
