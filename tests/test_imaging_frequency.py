import pandas as pd
import pytest
from analysis.contracts import Profile
from analysis.imaging_frequency import summarize_images


def fixture():
    images = pd.DataFrame([dict(source="image_object",event_key=f"{i}-{j}",patient_key=str(i),
        machine="M",event_start="2025-01-02 08:00",image_kind="cbct_unknown",image_seconds=6)
        for i in range(6) for j in range(2)])
    visits = pd.DataFrame([dict(patient_key=str(i),machine="Device",date="2025-01-02",duration=10+i) for i in range(6)])
    profile = Profile(machines={"M":"Device"})
    return images, {"visits":{"activity":visits}}, profile


def test_frequency_counts_objects_not_fields_and_does_not_guess_hypersight():
    images, prepared, profile = fixture()
    result = summarize_images(images,prepared,profile,{"image_objects_state":"AVAILABLE"})
    g = result["periods"]["year"]["activity"][0]["groups"][0]
    assert g["objects"] == 12 and g["matched_visits"] == 6
    assert g["objects_per_100_visits"] == 200
    assert g["kind"] == "cbct_unknown" and "Unbekannt" in g["equipment"]
    assert g["exposure_seconds"]["median"] == 6
    assert g["visit_duration_minutes"]["median"] == 12.5


def test_unmapped_images_are_source_audit_not_treatment_imaging():
    images, prepared, profile = fixture()
    images['machine'] = 'NA'
    images['image_kind'] = 'unknown'
    out = summarize_images(images, prepared, profile, {'image_objects_state':'AVAILABLE'})
    period = out['periods']['year']['activity'][0]
    assert period['groups'] == []
    assert period['unassigned'][0]['objects'] == 12
    assert period['unassigned'][0]['machine'] == 'Geraet fehlt / mehrdeutig'


def test_missing_source_is_not_zero_and_multiple_visits_are_ambiguous():
    images, prepared, profile = fixture()
    assert not summarize_images(images,prepared,profile,{})["available"]
    prepared["visits"]["activity"] = pd.concat([prepared["visits"]["activity"]]*2,ignore_index=True)
    g = summarize_images(images,prepared,profile,{"image_objects_state":"AVAILABLE"})["periods"]["year"]["activity"][0]["groups"][0]
    assert g["objects"] == 12 and g["matched_objects"] is None


def test_confirmed_dated_equipment_annotation_and_overlap_guard():
    images, prepared, profile = fixture()
    era=dict(machine="M",start="2025-01-01",end="2025-06-30",model="Halcyon",cbct_system="HyperSight",cbct_modality="kv",confirmed=True)
    profile=Profile(machines=profile.machines,equipment_periods=[era])
    g = summarize_images(images,prepared,profile,{"image_objects_state":"AVAILABLE"})["periods"]["year"]["activity"][0]["groups"][0]
    assert g["kind"] == "kv_cbct" and "HyperSight" in g["equipment"]
    with pytest.raises(ValueError,match="overlap"):
        Profile(machines=profile.machines,equipment_periods=[era,era])


def test_optional_sql_exports_no_image_label_or_original_identity():
    from tools.imaging_objects_v2 import query, FIELDS
    sql=query()
    assert 'sp_executesql' in sql and 'WHERE 1=0; RETURN' in sql
    assert not {"ImageId","ctrImageSer","DimPatientID","ImageUID"} & set(FIELDS)
    assert 'image_creation_not_acquisition' in sql
