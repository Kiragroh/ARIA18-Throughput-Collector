"""Build participant bundles from an explicit allowlist, never local exports."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUN_FILES = {
    'Durchfuehrung/README.md': 'kooperation/RDL_AUSFUEHREN.md',
    'Durchfuehrung/RDL_AUSFUEHREN.md': 'kooperation/RDL_AUSFUEHREN.md',
    'Durchfuehrung/START_HIER.html': 'kooperation/START_HIER.html',
    'Durchfuehrung/ARIA18_Throughput_Collector_2.0.rdl': 'dist/ARIA18_Throughput_Collector_2.0.rdl',
    'Durchfuehrung/Begleitbogen.md': 'kooperation/Begleitbogen.md',
    'Durchfuehrung/Upload_Checkliste.md': 'kooperation/Upload_Checkliste.md',
}


def manifest(analysis=True):
    files = {'README.md': 'PAKET_START.md' if analysis else 'PAKET_DURCHFUEHRUNG.md', **RUN_FILES}
    if analysis:
        files.update({
            'Analyse/README.md': 'docs/v2/PAKET_ANALYSE.md',
            'Analyse/requirements-analysis.txt': 'requirements-analysis.txt',
            'Analyse/method-v2.json': 'method-v2.json',
            'Analyse/profiles/site-template.json': 'profiles/site-template.json',
            'Analyse/profiles/synthetic.json': 'profiles/synthetic.json',
            'Analyse/tools/prepare_site.py': 'tools/prepare_site.py',
            'Analyse/tools/Standort_vorbereiten.cmd': 'tools/Standort_vorbereiten.cmd',
            'Analyse/tools/create_demo_v2.py': 'tools/create_demo_v2.py',
            'Analyse/tools/create_comparison_demo.py': 'tools/create_comparison_demo.py',
            'Analyse/tools/build_collector_v2.py': 'tools/build_collector_v2.py',
            'Analyse/tools/imaging_objects_v2.py': 'tools/imaging_objects_v2.py',
            'Analyse/tools/build_rdl.py': 'tools/build_rdl.py',
            'Analyse/docs/METHODIK.md': 'docs/v2/METHODIK.md',
            'Analyse/docs/AG_PROJEKT.md': 'docs/v2/AG_PROJEKT.md',
            'Analyse/docs/STANDORTVERGLEICH.md': 'docs/v2/STANDORTVERGLEICH.md',
            'Analyse/docs/VALIDIERUNG_RC6.md': 'docs/v2/VALIDIERUNG_RC6.md',
            'Analyse/docs/VALIDIERUNG_RC7.md': 'docs/v2/VALIDIERUNG_RC7.md',
        })
        for pattern in ('*.py', '*.html'):
            for path in sorted((ROOT / 'analysis').glob(pattern)):
                source = path.relative_to(ROOT).as_posix()
                files['Analyse/' + source] = source
    return dict(sorted(files.items()))


def package(analysis=True):
    contents = {name: (ROOT / source).read_bytes() for name, source in manifest(analysis).items()}
    contents['SHA256SUMS.txt'] = ''.join(
        hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
        for name, data in contents.items()).encode('ascii')
    name = 'ARIA-Performance_Gesamtpaket.zip' if analysis else 'ARIA-Performance_Durchfuehrung.zip'
    target = ROOT / 'packages' / name
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 9, 15, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data, compresslevel=9)
    target.with_suffix('.zip.sha256').write_text(
        hashlib.sha256(target.read_bytes()).hexdigest() + '  ' + target.name + '\n', encoding='ascii')
    print('PACKAGE_OK', target.name, len(contents), 'files')
    return target


if __name__ == '__main__':
    package()
    package(analysis=False)
