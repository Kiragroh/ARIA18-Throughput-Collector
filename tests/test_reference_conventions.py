import json
import pandas as pd
import pytest
from analysis.contracts import Profile


def events(repeated_course=False, inferred=6):
    rows = []
    for i in range(6):
        for j, (time, kind, source, status) in enumerate([
            ('2024-12-20', 'counselling', 'appointment', 'completed'),
            ('2025-01-03', 'counselling', 'appointment', 'completed'),
            ('2025-01-05', 'treatment_external', 'delivery', 'delivered'),
            ('2025-03-05', 'treatment_external', 'delivery', 'delivered'),
        ]):
            rows.append(dict(patient_key=f'p{i}', event_key=f'e{i}-{j}', event_start=time,
                event_end=time, kind=kind, source=source, status=status, activity_code=str(j),
                course_key='same' if repeated_course else f'course{j}', plan_key=f'plan{j}'))
    for i in range(inferred):
        for j, (time, kind, source) in enumerate([
            ('2025-01-01', 'counselling', 'appointment'),
            ('2025-01-02', 'treatment_brachy', 'appointment'),
        ]):
            rows.append(dict(patient_key=f'open{i}', event_key=f'o{i}-{j}', event_start=time,
                event_end=time, kind=kind, source=source, status='open' if j == 0 else 'completed',
                activity_code=str(j), course_key=None, plan_key=None))
    return pd.DataFrame(rows)


def compare(frame):
    from analysis.reconciliation import reference_conventions
    return reference_conventions(frame, Profile(), data_through='2026-06-01')


def test_reference_conventions_keep_first_cohort_separate_and_inference_explicit():
    result = compare(events())
    daily = result['variants'][0]
    assert daily['treatment_episodes'] == 18
    assert daily['documented_last_episodes'] == 6
    assert daily['inferred_episodes'] == 6
    assert daily['attended_episodes'] == 12
    assert daily['multiple_last_episodes'] == 6
    assert not any(key in json.dumps(result) for key in ['patient_key', 'event_key', 'course_key', 'plan_key'])


def test_course_intervals_do_not_merge_distinct_patients_and_manual_therapy_remains():
    result = compare(events(repeated_course=True))
    assert [v['treatment_episodes'] for v in result['variants']] == [18, 12]


def test_plan_fallback_does_not_put_all_missing_courses_in_one_course():
    frame = events()
    frame['course_key'] = None
    assert [v['treatment_episodes'] for v in compare(frame)['variants']] == [18, 18]


def test_reference_uses_calendar_day_and_does_not_count_cancelled_or_future_therapy():
    frame = events()
    frame.loc[frame.kind.eq('counselling') & frame.event_start.eq('2025-01-03'), 'event_start'] = '2025-01-05 12:00'
    frame.loc[frame.kind.eq('counselling') & frame.event_start.eq('2025-01-05 12:00'), 'event_end'] = '2025-01-05 13:00'
    frame = pd.concat([frame, frame.assign(event_key=lambda f:f.event_key+'future',
        event_start='2027-01-01', event_end='2027-01-01')], ignore_index=True)
    cancelled = frame[frame.source.eq('delivery')].copy()
    cancelled['patient_key'] += '-cancelled'
    cancelled['event_key'] += '-cancelled'
    cancelled['status'] = 'cancelled'
    frame = pd.concat([frame,cancelled], ignore_index=True)
    daily = compare(frame)['variants'][0]
    assert daily['multiple_last_episodes'] == 6
    assert daily['treatment_episodes'] == 18


def test_tiny_inferred_partition_is_not_recoverable_from_total():
    variants = compare(events(inferred=1))['variants']
    for row in variants:
        assert row['attended_episodes'] is None
        assert row['inferred_episodes'] is None
        assert row['documented_last_episodes'] == 6


def test_small_difference_between_definitions_is_suppressed():
    frame = events()
    frame.loc[frame.patient_key.eq('p0'), 'course_key'] = 'same'
    variants = compare(frame)['variants']
    assert variants[0]['treatment_episodes'] == 18
    assert variants[1]['treatment_episodes'] is None


def test_source_exclusions_are_partitioned_without_patient_ids():
    from analysis.reconciliation import source_filter_audit
    frame = pd.DataFrame([dict(source='delivery', patient_class=kind, patient_key=str(i),
        event_start='2025-01-02', status='delivered', resource_status='')
        for kind in ['test_name','clinical_other','clinical_numeric'] for i in range(6)])
    counts = source_filter_audit(frame, Profile(require_numeric_patient_id=True))
    assert counts['selected']['test_name'] == 6
    assert counts['selected']['non_numeric_id'] == 6
    assert counts['selected']['retained'] == 6
    assert sum(counts['selected'].values()) == len(frame)
    assert 'patient_key' not in json.dumps(counts)


def test_image_objects_are_not_patient_filter_population_counts():
    from analysis.reconciliation import source_filter_audit
    frame = pd.DataFrame([dict(source='image_object',patient_class='test_name',
        event_start='2025-01-01',status='',patient_key='x')])
    assert sum(source_filter_audit(frame, Profile())['selected'].values()) == 0


def test_cancelled_appointments_are_retained_even_with_cancelled_resource():
    from analysis.reconciliation import source_filter_audit
    frame = pd.DataFrame([dict(source='appointment',patient_class='clinical_numeric',
        event_start='2025-01-01',status='Cancelled',resource_status='Cancelled',patient_key=str(i))
        for i in range(6)])
    assert source_filter_audit(frame, Profile())['selected']['retained'] == 6


def test_missing_source_flags_are_reported_as_unavailable_not_verified():
    from analysis.reconciliation import source_filter_audit
    frame = pd.DataFrame([dict(source='delivery',event_start='2025-01-01',status='delivered')])
    result = source_filter_audit(frame, Profile())
    assert result['patient_class_available'] is False
    assert result['resource_status_available'] is False


@pytest.mark.parametrize('available', [True, False])
def test_cli_imaging_label_follows_actual_export_capability(tmp_path, monkeypatch, available):
    from analysis import cli
    from tools.create_demo_v2 import create
    from analysis.ingest import load_export
    path = tmp_path/'demo.xlsx'
    create(path)
    metadata, frame, coverage, catalog = load_export(path)
    frame = frame.iloc[:80].copy()
    metadata['image_objects_state'] = 'AVAILABLE' if available else 'UNAVAILABLE'
    monkeypatch.setattr(cli, 'load_export', lambda path:(metadata,frame,coverage,catalog))
    profile = Profile(machines={f'M{i}':f'Device {i}' for i in range(1,5)},
        activity_codes={'TX':'treatment_external','CONS':'counselling','RETURN':'observation'})
    data = cli.analyze(path, profile)
    assert ('FactPatientImage' in data['quality']['imaging_source']) is available
    assert 'reference_conventions' in data['flow']
    assert 'source_filters' in data['quality']
