"""Evaluate generated guard expressions with a synthetic metadata catalogue."""
import re
import sqlite3

import pytest

from tools import build_collector_v2 as collector
from tools import build_preflight_v2 as preflight
from tools import imaging_objects_v2 as imaging


def evaluate(expression, *, absent=(), denied=(), unknown_permission=()):
    absent,denied,unknown_permission=map(set,(absent,denied,unknown_permission))
    db=sqlite3.connect(':memory:')
    db.create_function('COL_LENGTH',2,lambda table,column:None if (table,column) in absent else 8)
    db.create_function('HAS_PERMS_BY_NAME',5,lambda table,kind,perm,column,subkind:
        None if (table,column) in unknown_permission else int((table,column) not in denied))
    try:
        sql=re.sub(r"\bN'", "'", expression)
        return db.execute('SELECT CASE WHEN '+sql+' THEN 1 ELSE 0 END').fetchone()[0]
    finally:
        db.close()


def initial_guard(sql):
    return sql.split('IF ',1)[1].split('\nBEGIN',1)[0]


@pytest.mark.parametrize('dataset',['HistoryStatusInventory','CompletionDiagnostics'])
@pytest.mark.parametrize('column',['DimActivityTransactionID','ScheduledActivityHstryDateTime','ScheduledActivityCode'])
@pytest.mark.parametrize('state',['absent','denied','unknown_permission'])
def test_missing_history_is_unavailable_not_an_available_zero(dataset,column,state):
    sql,_=preflight.queries()[dataset]
    assert evaluate(initial_guard(sql),**{state:[('DWH.DimActivityTransactionHistory',column)]}) == 1


@pytest.mark.parametrize('state',['absent','denied','unknown_permission'])
@pytest.mark.parametrize('key',[(table,column) for table,cols in collector.SOURCES.values() for column,_,required in cols if required])
def test_required_sources_need_metadata_and_effective_read_permission(state,key):
    assert evaluate(collector.source_gaps(),**{state:[key]}) == 1


def test_optional_sources_do_not_block_core_collection():
    absent=[('DWH.DimActivityTransactionHistory','ScheduledActivityCode'),
            ('DWH.FactPatientImage','ImageCreationDate'),('DWH.DimPlan','NoFractionsPlanned')]
    assert evaluate(collector.source_gaps(),absent=absent,denied=absent) == 0


def test_delivery_evidence_requires_one_readable_alternative():
    table='DWH.FactTreatmentHistory'
    denied=[(table,c) for c in ('DeliveredMU','FieldMUActual','DoseDelivered')]
    assert evaluate(collector.source_gaps(),denied=denied) == 1
    assert evaluate(collector.source_gaps(),denied=denied[:2]) == 0


def test_optional_image_permission_failure_only_disables_image_dataset():
    denied=[('DWH.FactPatientImage','ImageCreationDate')]
    assert evaluate(imaging.missing(),denied=denied) == 1
    assert evaluate(collector.source_gaps(),denied=denied) == 0


def test_capabilities_include_optional_images_and_separate_permission_from_schema():
    sql=collector.capabilities()
    for col in ['ImageCreationDate','ImageId','ImageType','ExposureTime','ctrImageSer','FactPatientImageID']:
        assert "(N'DWH.FactPatientImage',N'"+col+"',0)" in sql
    assert 'AS schema_available' in sql
    assert 'AS select_allowed' in sql
    assert 'HAS_PERMS_BY_NAME' in sql


def test_stage_optional_projections_and_filters_are_permission_aware():
    assert "HAS_PERMS_BY_NAME(N'DWH.DimActivityTransaction',N'OBJECT',N'SELECT',N'ActivityEndDateTime',N'COLUMN')" in collector.stage('Appointment')
    assert "HAS_PERMS_BY_NAME(N'DWH.DimPlan',N'OBJECT',N'SELECT',N'DimPlanID',N'COLUMN')" in collector.stage('Plan')
    assert "HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ExposureTime',N'COLUMN')" in imaging.query()
