import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

from tools.package_v2 import RUN_FILES, manifest, package


def test_two_packages_share_exact_execution_files_and_have_no_exports():
    with zipfile.ZipFile(package()) as full, zipfile.ZipFile(package(False)) as small:
        assert set(full.namelist()) == set(manifest()) | {'SHA256SUMS.txt'}
        assert set(small.namelist()) == set(manifest(False)) | {'SHA256SUMS.txt'}
        for name in RUN_FILES:
            assert full.read(name) == small.read(name)
        assert all(not n.startswith('Analyse/') for n in small.namelist())
        assert 'Analyse/analysis/cli.py' in full.namelist()
        assert 'Analyse/analysis/compare.py' in full.namelist()
        assert 'Analyse/tools/create_comparison_demo.py' in full.namelist()
        assert 'Analyse/docs/STANDORTVERGLEICH.md' in full.namelist()
        assert not any(n.endswith(('.xlsx', '.csv', '.sqlite', '.log')) for n in full.namelist())
        for archive in (full, small):
            for line in archive.read('SHA256SUMS.txt').decode('ascii').splitlines():
                digest, name = line.split('  ', 1)
                assert hashlib.sha256(archive.read(name)).hexdigest() == digest


def test_package_is_repeatable_and_relative_markdown_links_resolve():
    first = package().read_bytes()
    assert package().read_bytes() == first
    for mode in (True, False):
        with zipfile.ZipFile(package(mode)) as archive:
            names = set(archive.namelist())
            for name in names:
                if not name.endswith('.md'):
                    continue
                for link in re.findall(r'\]\(([^)]+)\)', archive.read(name).decode('utf-8')):
                    if '://' in link or link.startswith('#'):
                        continue
                    resolved = (PurePosixPath(name).parent / link.split('#')[0]).as_posix()
                    assert resolved in names, (name, link)


def test_unpacked_analysis_runs_without_source_checkout(tmp_path):
    with zipfile.ZipFile(package()) as archive:
        archive.extractall(tmp_path)
    working = tmp_path / 'Analyse'
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    for arguments in (
        ['tools/create_demo_v2.py', '--output', 'Demo.xlsx'],
        ['-m', 'analysis.cli', 'Demo.xlsx', '--profile', 'profiles/synthetic.json',
         '--output', 'Demo-Ergebnis'],
        ['tools/create_comparison_demo.py', '--output', 'Vergleich-Demo'],
        ['-m', 'analysis.compare', '--site', 'A=Vergleich-Demo/DEMO-1.json',
         '--site', 'B=Vergleich-Demo/DEMO-2.json', '--output', 'Vergleich-CLI'],
    ):
        result = subprocess.run([sys.executable, *arguments], cwd=working, env=env,
                                capture_output=True, text=True, timeout=180)
        assert result.returncode == 0, result.stdout + result.stderr
    assert (working / 'Demo-Ergebnis/Standortanalyse.html').is_file()
    assert (working / 'Demo-Ergebnis/aggregate.json').is_file()
    aggregate = json.loads((working / 'Demo-Ergebnis/aggregate.json').read_text(encoding='utf-8'))
    assert aggregate['provenance']['synthetic'] is True
    assert len(aggregate['provenance']['analysis_sha256']) == 64
    comparison = json.loads((working / 'Vergleich-CLI/Vergleich.json').read_text(encoding='utf-8'))
    assert len(comparison['sites']) == 2
    assert 'local_review_missing' in comparison['checks'][0]['domains']['throughput']['reasons']
    assert (working / 'Vergleich-Demo/Vergleich/Standortvergleich.html').is_file()


def test_public_downloads_are_complete_bundles_not_single_rdl():
    root = Path(__file__).resolve().parents[1]
    for name in ('README.md', 'kooperation/README.md', 'templates/Cooperation.template.html'):
        text = (root / name).read_text(encoding='utf-8')
        assert 'ARIA-Performance_Gesamtpaket.zip' in text
        assert 'ARIA-Performance_Durchfuehrung.zip' in text
        assert not re.search(r'releases/download/[^/]+/[^\s"<>)]*\.rdl', text)
