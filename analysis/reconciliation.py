"""Aggregate-only checks of source exclusions and operational counting conventions."""
from collections import defaultdict
import pandas as pd
from .metrics import deduplicate


def source_filter_audit(events, profile):
    frame = events[~events.source.eq('image_object')].copy()
    reasons = pd.Series('retained', index=frame.index)
    if 'resource_status' in frame:
        inactive = frame.resource_status.fillna('').str.casefold().isin(['deleted','cancelled'])
        reasons.loc[inactive & ~frame.status.map(profile.classify_status).eq('cancelled')] = 'inactive_resource'
    if 'patient_class' in frame:
        if profile.require_numeric_patient_id:
            reasons.loc[~frame.patient_class.isin(['clinical_numeric','no_patient','unknown'])] = 'non_numeric_id'
        reasons.loc[frame.patient_class.eq('test_name')] = 'test_name'
    dates = pd.to_datetime(frame.event_start, errors='coerce', format='mixed').dt.strftime('%Y-%m-%d')
    result = dict(numeric_id_required=profile.require_numeric_patient_id,
                  patient_class_available=bool('patient_class' in frame and frame.patient_class.notna().any()),
                  resource_status_available=bool('resource_status' in frame and frame.resource_status.notna().any()),
                  unit='export_event_rows_excluding_image_objects')
    for name, scope in [('selected', dates.between(profile.start, profile.end)),
                        ('context', pd.Series(True, index=frame.index))]:
        counts = reasons[scope].value_counts()
        result[name] = {reason: (f'<{profile.minimum_patients}' if 0 < int(counts.get(reason,0)) < profile.minimum_patients
                                else int(counts.get(reason,0)))
                        for reason in ['retained','test_name','non_numeric_id','inactive_resource']}
    return result


def _merge_intervals(intervals):
    result = defaultdict(list)
    for patient, start, end in sorted(intervals):
        current = result[patient]
        if current and start <= current[-1][1] + pd.Timedelta(days=30):
            current[-1][1] = max(end, current[-1][1])
        else:
            current.append([start,end])
    return result


def _operational_counts(episodes, consults, profile):
    names = ['treatment_episodes','documented_last_episodes','inferred_episodes',
             'attended_episodes','multiple_last_episodes']
    counts = dict.fromkeys(names, 0)
    patients = {name:set() for name in names}
    start, end = pd.Timestamp(profile.start), pd.Timestamp(profile.end)
    for patient, periods in episodes.items():
        selected = [a for a,b in periods if start <= a <= end]
        counts['treatment_episodes'] += len(selected)
        if selected:
            patients['treatment_episodes'].add(patient)
    for patient, group in consults.groupby('patient_key'):
        periods = episodes.get(patient, [])
        chains = defaultdict(list)
        for row in group.sort_values('_time').itertuples(index=False, name=None):
            time, status = row
            next_index = next((i for i,(a,b) in enumerate(periods) if a >= time), None)
            previous = max((i for i,(a,b) in enumerate(periods) if a < time), default=-1)
            key = ('next',next_index) if next_index is not None else ('unmatched',previous)
            chains[key].append((time,status))
        for key, chain in chains.items():
            completed = [time for time,status in chain if status == 'completed']
            if completed:
                when, evidence = completed[-1], 'documented_last_episodes'
            elif key[0] == 'next':
                when, evidence = chain[0][0], 'inferred_episodes'
            else:
                continue
            if not start <= when <= end:
                continue
            for name in ['attended_episodes', evidence]:
                counts[name] += 1
                patients[name].add(patient)
            if key[0] == 'next' and len(completed) > 1:
                counts['multiple_last_episodes'] += 1
                patients['multiple_last_episodes'].add(patient)
    for name in names:
        if counts[name] and len(patients[name]) < profile.minimum_patients:
            counts[name] = None
    # The total must not reveal a small documented/inferred component by subtraction.
    if any(counts[name] is None for name in ['documented_last_episodes','inferred_episodes']):
        counts['attended_episodes'] = None
    return counts


def reference_conventions(flow_events, profile, *, data_through):
    """Keep sensitivity counts separate; never overwrite the prespecified cohort."""
    frame, _ = deduplicate(flow_events)
    frame = frame[frame.patient_key.notna() & frame.patient_key.ne('')].copy()
    times = pd.to_datetime(frame.event_start, errors='coerce', format='mixed')
    ends = pd.to_datetime(frame.event_end, errors='coerce', format='mixed').fillna(times)
    if 'milestone_time' in frame:
        milestone = pd.to_datetime(frame.milestone_time, errors='coerce', format='mixed')
        manual = frame.source.eq('appointment') & milestone.notna()
        times.loc[manual], ends.loc[manual] = milestone[manual], milestone[manual]
    frame['_time'], frame['_end'] = times.dt.normalize(), ends.dt.normalize()
    frame['_status'] = frame.status.map(profile.classify_status)
    treatment = frame[frame.kind.str.startswith('treatment') & frame['_status'].eq('completed')
                      & times.notna() & ends.ge(times) & times.lt(pd.Timestamp(data_through)+pd.Timedelta(days=1))]
    day_intervals = list(treatment[['patient_key','_time','_end']].itertuples(index=False, name=None))
    courses = defaultdict(list)
    course_intervals = []
    for row in treatment.to_dict('records'):
        if row['source'] != 'delivery':
            course_intervals.append((row['patient_key'],row['_time'],row['_end']))
            continue
        identity = next(((name,str(row[name])) for name in ['course_key','plan_key','event_key']
                         if pd.notna(row.get(name)) and str(row.get(name,''))), None)
        if identity is None:
            course_intervals.append((row['patient_key'],row['_time'],row['_end']))
        else:
            courses[(row['patient_key'],identity)].append((row['_time'],row['_end']))
    course_intervals += [(patient,min(a for a,b in spans),max(b for a,b in spans))
                         for (patient,identity),spans in courses.items()]
    consults = frame[frame.kind.eq('counselling') & frame['_status'].isin(['completed','open'])
                     & frame['_time'].notna()].set_index('patient_key')[['_time','_status']]
    variants = []
    for definition, intervals in [('treatment_days_30d',day_intervals),('aria_courses_30d',course_intervals)]:
        counts = _operational_counts(_merge_intervals(intervals), consults, profile)
        variants.append(dict(definition=definition, **counts))
    # Do not publish tiny differences between two definitions of the same count.
    for name, value in variants[1].items():
        other = variants[0].get(name)
        if isinstance(value,int) and isinstance(other,int) and 0 < abs(value-other) < profile.minimum_patients:
            variants[1][name] = None
    if any(row['attended_episodes'] is None for row in variants):
        for row in variants:
            row['attended_episodes'] = None
    return dict(method='operational_reference_v1', variants=variants)
