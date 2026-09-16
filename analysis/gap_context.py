"""Calendar context within measured treatment gaps; not evidence of actual work."""
import pandas as pd


def collect(rows, gaps, output):
    for row in rows.itertuples():
        if pd.isna(row.event_start) or pd.isna(row.event_end):
            continue
        a,b = row.event_start.timestamp()/60,row.event_end.timestamp()/60
        overlap = sum(max(0,min(b,y)-max(a,x)) for x,y in gaps if y-x >= 30)
        if overlap <= 0:
            continue
        key = (str(row.activity_code), str(row.kind))
        entry = output.setdefault(key, dict(events=set(),patients=set(),minutes=0.0))
        entry['events'].add(row.Index)
        if row.patient_key:
            entry['patients'].add(row.patient_key)
        entry['minutes'] += overlap


def publish(context, minimum, safe):
    return [dict(code=code,kind=kind,
                 appointments=len(v['events']) if safe and (not v['patients'] or len(v['patients'])>=minimum) else None,
                 overlap_minutes=v['minutes'] if safe and (not v['patients'] or len(v['patients'])>=minimum) else None)
            for (code,kind),v in sorted(context.items())]
