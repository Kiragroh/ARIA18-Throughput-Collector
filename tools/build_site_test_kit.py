"""Package only the files needed for a no-Python first-site test."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'README.md': 'kooperation/RDL_AUSFUEHREN.md',
    'START_HIER.html': 'kooperation/START_HIER.html',
    'ARIA18_Standort_Preflight_2.0.rdl': 'dist/ARIA18_Standort_Preflight_2.0.rdl',
    'ARIA18_Throughput_Collector_2.0.rdl': 'dist/ARIA18_Throughput_Collector_2.0.rdl',
}


def build():
    contents = {name: (ROOT / source).read_bytes() for name, source in FILES.items()}
    sums = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
                   for name, data in contents.items())
    contents['SHA256SUMS.txt'] = sums.encode('ascii')
    target = ROOT / 'packages/ARIA-Performance_Standorttest.zip'
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 9, 15, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    target.with_suffix('.zip.sha256').write_text(
        hashlib.sha256(target.read_bytes()).hexdigest() + '  ' + target.name + '\n', encoding='ascii')
    print('SITE_TEST_KIT_OK', len(contents), 'files', target.stat().st_size, 'bytes')
    return target


if __name__ == '__main__':
    build()
