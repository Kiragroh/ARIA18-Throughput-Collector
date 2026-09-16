import pandas as pd
import pytest
from analysis.ingest import enrich_images
from analysis.imaging import classify
from tools.image_acquisition_v2 import query


def test_brainlab_rtimage_is_exactrac_but_reference_wins():
    kw = dict(image_type='ImagePI',modality='RTIMAGE',task='DICOM Service',manufacturer='Brainlab',dosimeter='MU')
    assert classify(**kw)['class'] == 'ExacTrac'
    assert classify(**kw,reference_image=True)['class'] == 'reference'
    assert classify(image_type='Image',modality='CT',task='DICOM Service',manufacturer='Varian')['class'] == 'unverified_CT'


def test_native_enrichment_requires_same_image_not_patient_day():
    events = pd.DataFrame([dict(source='image_object',event_key='a',image_kind='unknown_2d',machine='M'),
                           dict(source='image_object',event_key='b',image_kind='unknown',machine='NA')])
    record = dict(run_id='r',source_state='AVAILABLE',event_key='a',acquisition_kind='exactrac_2d',
                  image_manufacturer='Brainlab',acquisition_machine=None,acquisition_time='2025-01-02')
    out = enrich_images(events,[record],dict(run_id='r'))
    assert out.image_kind.tolist() == ['exactrac_2d','unknown']
    assert out.machine.tolist() == ['M','NA']
    with pytest.raises(ValueError,match='run identity'):
        enrich_images(events,[record],dict(run_id='different'))
    with pytest.raises(ValueError,match='Conflicting'):
        enrich_images(events,[record,dict(record,acquisition_kind='mv_2d')],dict(run_id='r'))


def test_native_query_guards_source_and_excludes_ct_slices():
    sql = query()
    assert 'sp_executesql' in sql and 'HAS_PERMS_BY_NAME' in sql
    assert "N'%BRAINLAB%'".replace("'","''") in sql
    assert 'PatientSer' not in sql and 'ImageId' not in sql
    assert 'ImageCT' not in sql
