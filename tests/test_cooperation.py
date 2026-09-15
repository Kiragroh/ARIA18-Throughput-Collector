from pathlib import Path
import re
import zipfile
from tools.build_cooperation import build

ROOT=Path(__file__).resolve().parents[1]
UPLOAD='https://filesync.medizin.uni-leipzig.de/u/d/7aa97de1de02445cad42/'


def test_invitation_is_self_contained_and_has_upload_boundary():
    html=(ROOT/'kooperation/index.html').read_text(encoding='utf-8')
    assert html.count('class="slide')==7
    assert '__QR_DATA__' not in html and '__CHART_DATA__' not in html and '__PROJECT_QR_DATA__' not in html
    assert html.count('data:image/png;base64,')==3
    assert UPLOAD in html and 'Nicht hochladen' in html
    assert 'Patientenlisten' in html and 'Original-Fall-/Plan-IDs' in html
    assert 'Synthetisches Beispiel' in html
    assert 'STANDORT_Phase_VON-BIS_R01.zip' in html
    assert 'Upload-Benachrichtigungen' in html and 'Maximilian Grohmann' in html
    assert 'QR-Code zur GitHub-Projektseite' in html
    assert not re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://',html)


def test_cooperation_archive_is_explicitly_allowlisted():
    path=build()
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist())==9
        assert all(n.startswith('kooperation/') for n in archive.namelist())
        assert not any(n.endswith(('.csv','.xlsx','.sqlite','.json')) for n in archive.namelist())


def test_submission_identity_is_required_and_portable_links_resolve():
    readme=(ROOT/'kooperation/README.md').read_text(encoding='utf-8')
    form=(ROOT/'kooperation/Begleitbogen.md').read_text(encoding='utf-8')
    assert 'MUSTER-STR_Standorttest_20250101-20251231_R01.zip' in readme
    assert 'nicht automatisch' in readme
    for field in ['Einreichungs-ID','Ersetzt Einreichungs-ID','Rueckmeldeadresse (optional',
                  'ARIA-Version (optional','Enthaltene Dateien','Vollstaendiger Klinikname']:
        assert field in form
    assert '../' not in readme


def test_startpage_describes_current_workflow_only():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    assert '2.0.0-rc.5' in readme and 'kooperation/README.md' in readme
    assert 'docs/assets/banner-github.png' in readme
    assert (ROOT/'docs/assets/banner-github.png').is_file()
    assert 'analyze_single_site.py' not in readme
    assert 'ARIA18_Durchsatz_Klinikvergleich_Collector.rdl' not in readme
    assert readme.index('Dieses Projekt') < readme.index('kooperation/README.md')
    assert 'Upload-Benachrichtigungen' in readme
