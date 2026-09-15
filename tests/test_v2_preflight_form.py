import json
from openpyxl import Workbook
from tools.prepare_site import create
from analysis.contracts import Profile


def test_preflight_form_only_embeds_allowlisted_inventory(tmp_path):
    wb=Workbook();wb.remove(wb.active)
    tables={
        '00_Metadata':[['contract_version'],['2.0']],
        '01_Capabilities':[['contract_version','source_name','column_name','available','is_required'],['2.0','Source','Time',0,0]],
        '02_Activities':[['activity_code','activity_name','activity_category'],['CONS','Consultation','Clinical']],
        '03_AppointmentInventory':[['source_state','activity_code','appointment_status','machine','distinct_appointments'],['AVAILABLE','CONS','Complete','M1',25]],
        '04_MachineInventory':[['source_state','machine'],['AVAILABLE','M1']],
        'Private':[['patient_key'],['DO_NOT_EMBED']],
    }
    for title,rows in tables.items():
        sheet=wb.create_sheet(title)
        for row in rows:sheet.append(row)
    path=tmp_path/'preflight.xlsx';wb.save(path)
    output=create(path,tmp_path/'setup')
    html=output.read_text(encoding='utf-8')
    assert 'DO_NOT_EMBED' not in html
    assert 'Consultation' in html and 'M1' in html
    assert '"confirmed": false' in html


def test_local_status_override_does_not_require_sql_changes():
    profile=Profile(status_codes={'Locally finished':'completed'})
    assert profile.classify_status('Locally finished')=='completed'
    assert profile.classify_status('Pending')=='open'
