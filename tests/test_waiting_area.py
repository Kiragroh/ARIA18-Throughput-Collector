from tools import waiting_area_v2 as waiting


def test_optional_waiting_source_uses_history_not_today_view():
    sql=waiting.query()
    assert 'PatientLocationMH' in sql and 'CheckedInFlag=1' in sql
    assert 'GETDATE' not in sql and 'vv_PatientWaitTime' not in sql
    assert 'UNAVAILABLE' in sql and 'BEGIN CATCH' in sql
    assert 'COUNT(DISTINCT PatientSer)>=5' in sql
    assert 'CROSS_DAY' in sql and 'OVER_240_MIN' in sql
    assert not any('patient' in x.lower() and x!='patients' for x in waiting.FIELDS)
