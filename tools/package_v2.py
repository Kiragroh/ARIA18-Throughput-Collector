"""Build an explicit-allowlist package. Never include exports, caches or logs."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def package():
    version=json.loads((ROOT/"method-v2.json").read_text())["release"]
    paths=["README.md","PAKET_START.md","CHANGELOG.md","requirements-analysis.txt","method-v2.json",
           "dist/ARIA18_Throughput_Collector_2.0.rdl","dist/ARIA18_Throughput_Collector_Fast_2.0.rdl",
           "dist/ARIA18_Imaging_Preflight_2.0.rdl",
           "dist/ARIA18_Standort_Preflight_2.0.rdl","tools/build_preflight_v2.py",
           "tools/prepare_site.py","tools/Standort_vorbereiten.cmd",
           "tools/check_preflight_form.cjs",
           "tools/build_collector_v2.py","tools/build_imaging_preflight.py","tools/build_fast_collector_v2.py","tools/build_rdl.py",
           "tools/create_demo_v2.py","tools/test_collector_v2.ps1","tools/check_report.cjs",
           "tools/package_v2.py","templates/ARIA18_Collector.template.rdl"]
    for folder,pattern in [("analysis","*.py"),("analysis","*.html"),("docs/v2","*.md"),
                           ("profiles","*.json"),("sql/v2","*.sql"),("tests","test_v2*.py")]:
        paths.extend(str(p.relative_to(ROOT)).replace("\\","/") for p in (ROOT/folder).glob(pattern))
    paths=sorted(set(paths))
    output=ROOT/"packages";output.mkdir(exist_ok=True)
    target=output/("ARIA18-Throughput-"+version+".zip")
    checksums={}
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for relative in paths:
            content=(ROOT/('PAKET_START.md' if relative=='README.md' else relative)).read_bytes()
            checksums[relative]=hashlib.sha256(content).hexdigest()
            z.writestr(relative,content)
        z.writestr("SHA256SUMS.txt","\n".join(f"{sha}  {name}" for name,sha in checksums.items())+"\n")
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(sha+"  "+target.name+"\n",encoding="ascii")
    print("PACKAGE_OK files="+str(len(paths))+" sha256="+sha)
    return target


if __name__=="__main__":
    package()
