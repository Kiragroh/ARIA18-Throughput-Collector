"""Build a self-contained invitation and a separate, non-clinical cooperation ZIP."""
import base64
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def build(check=False):
    html=(ROOT/'templates/Cooperation.template.html').read_text(encoding='utf-8')
    release=json.loads((ROOT/'release-v2.json').read_text(encoding='utf-8'))
    html=html.replace('__PACKAGE_VERSION__',release['package_version'])
    for token,name in [('__QR_DATA__','qr-code.png'),('__PROJECT_QR_DATA__','projekt-qr-code.png'),
                       ('__CHART_DATA__','boxplots-beispiel.png')]:
        image=(ROOT/'kooperation/assets'/name).read_bytes()
        html=html.replace(token,'data:image/png;base64,'+base64.b64encode(image).decode('ascii'))
    page=ROOT/'kooperation/index.html'
    if check:
        if not page.exists() or page.read_text(encoding='utf-8') != html:
            raise ValueError('Generated cooperation page is outdated; run tools/build_cooperation.py')
        print('COOPERATION_CURRENT')
        return page
    page.write_text(html,encoding='utf-8')
    output=ROOT/'packages';output.mkdir(exist_ok=True)
    (output/'Kooperation_ARIA_Performance.html').write_text(html,encoding='utf-8')
    path=output/'ARIA-Performance_Kooperation.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ['README.md','Begleitbogen.md','Upload_Checkliste.md','RDL_AUSFUEHREN.md','START_HIER.html','index.html',
                     'assets/qr-code.png','assets/projekt-qr-code.png','assets/boxplots-beispiel.png']:
            file=ROOT/'kooperation'/name
            z.write(file,file.relative_to(ROOT).as_posix())
    path.with_suffix('.zip.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n',encoding='ascii')
    print('COOPERATION_BUILD_OK')
    return path


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check the committed page without changing files')
    build(check=parser.parse_args().check)
