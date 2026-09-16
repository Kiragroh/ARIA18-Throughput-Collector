import pandas as pd
from analysis.contracts import Profile
from analysis.ingest import normalize_flow
from tools.build_collector_v2 import SOURCES, FIELDS, event_sql, stage


def test_fallback_uses_transaction_identity_and_optional_revision_columns():
    sql = event_sql()
    assert 'n.ctrActivitySer=a.ctrActivitySer' in sql
    assert 'n.ctrActivitySer=act.ctrActivitySer' not in sql
    assert 'ORDER BY n.ActivityRevCount DESC,n.DimActivityID DESC' in sql
    assert 'n.ActivityRevCount IS NOT NULL' in sql
    assert "NULLIF(LTRIM(RTRIM(act.ActivityNameDEU)),N'') IS NULL" in sql
    assert "UPPER(LTRIM(RTRIM(act.ActivityNameDEU)))=N'NA'" in sql
    for source, column in [('Appointment','ctrActivitySer'),('Activity','ctrActivitySer'),('Activity','ActivityRevCount')]:
        assert next(required for name, _, required in SOURCES[source][1] if name == column) is False
        assert 'CAST(NULL AS' in stage(source)
    for field in ['activity_name_original','activity_name_source','activity_name_revision']:
        assert field in FIELDS and field in sql
    assert 'act.ActivityCode' in sql


def test_resolved_external_slot_is_not_an_additional_rv_fraction():
    profile=Profile(activity_names={'Bestrahlung ETHOS adaptiv':'treatment_external'})
    events=pd.DataFrame([
        dict(source='delivery',patient_key='p',machine='device',activity_code='',activity_name='',is_brachy=0),
        dict(source='appointment',patient_key='p',machine='device',activity_code='NA',
             activity_name='Bestrahlung ETHOS adaptiv',activity_name_original='NA',is_brachy=0),
    ])
    assert profile.classify_activities(events).iloc[1]=='treatment_external'
    flow=normalize_flow(events,profile)
    assert len(flow)==1 and flow.iloc[0].source=='delivery'
