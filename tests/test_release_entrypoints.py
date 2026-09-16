import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile
import pytest

from analysis import VERSION
from tools.build_collector_v2 import COLLECTOR_RELEASE
from tools.build_cooperation import build
from tools import build_cooperation
from tools.package_v2 import package

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / 'release-v2.json').read_text(encoding='utf-8'))


def test_release_identifies_unchanged_tested_collector_and_analysis():
    assert RELEASE['collector_release'] == COLLECTOR_RELEASE
    assert RELEASE['analysis_version'] == VERSION
    rdl = ROOT / 'dist/ARIA18_Throughput_Collector_2.0.rdl'
    assert RELEASE['collector_sha256_lf'] == hashlib.sha256(rdl.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def test_current_entrypoints_only_link_assets_of_current_package():
    build()
    for name in ('README.md', 'kooperation/README.md', 'kooperation/RDL_AUSFUEHREN.md', 'kooperation/index.html'):
        text = (ROOT / name).read_text(encoding='utf-8')
        links = re.findall(r'releases/download/v([^/]+)/([^\s"<>)]*)', text)
        assert links, name
        assert all(version == RELEASE['package_version'] for version, _ in links), name
        assert all(asset in RELEASE['release_assets'] for _, asset in links), name
        assert '__PACKAGE_VERSION__' not in text
    form = (ROOT / 'kooperation/START_HIER.html').read_text(encoding='utf-8')
    assert 'Paket ' + RELEASE['package_version'] in form
    for name in ('PAKET_START.md', 'PAKET_DURCHFUEHRUNG.md'):
        assert RELEASE['package_version'] in (ROOT / name).read_text(encoding='utf-8').splitlines()[0]


def test_bundles_include_release_identity_and_current_offline_form():
    for mode in (True, False):
        with ZipFile(package(mode)) as archive:
            assert json.loads(archive.read('release-v2.json')) == RELEASE
            form = archive.read('Durchfuehrung/START_HIER.html').decode('utf-8')
            assert 'Paket ' + RELEASE['package_version'] in form
            rdl = archive.read('Durchfuehrung/ARIA18_Throughput_Collector_2.0.rdl')
            assert hashlib.sha256(rdl.replace(b'\r\n', b'\n')).hexdigest() == RELEASE['collector_sha256_lf']


def test_participation_describes_runtime_and_correction_loop():
    for name in ('README.md', 'kooperation/README.md', 'kooperation/RDL_AUSFUEHREN.md'):
        text = (ROOT / name).read_text(encoding='utf-8')
        assert 'drei Minuten' in text, name
        assert 'RDL' in text and 'JSON' in text and 'Excel' in text


def test_generated_page_check_rejects_stale_file_without_rewriting(tmp_path, monkeypatch):
    for name in ('templates/Cooperation.template.html', 'release-v2.json',
                 'kooperation/assets/qr-code.png', 'kooperation/assets/projekt-qr-code.png',
                 'kooperation/assets/boxplots-beispiel.png'):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    page = tmp_path / 'kooperation/index.html'
    page.write_text('stale page', encoding='utf-8')
    monkeypatch.setattr(build_cooperation, 'ROOT', tmp_path)
    with pytest.raises(ValueError, match='outdated'):
        build_cooperation.build(check=True)
    assert page.read_text(encoding='utf-8') == 'stale page'
    shutil.copyfile(ROOT / 'kooperation/index.html', page)
    assert build_cooperation.build(check=True) == page
    assert not (tmp_path / 'packages').exists()
