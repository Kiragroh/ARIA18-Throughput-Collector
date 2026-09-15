"""Time intervals and counts. No original identifiers leave this module."""
import math
import re
import pandas as pd
import numpy as np


def natural_key(value):
    return [int(t) if t.isdigit() else t.casefold() for t in re.split(r"(\d+)", str(value))]


def deduplicate(frame):
    if frame.empty:
        return frame.copy(), dict(raw_rows=0, exact_duplicates=0, natural_duplicates=0, conflicting_keys=0, missing_keys=0)
    clean = frame.drop_duplicates().copy()
    audit = dict(raw_rows=len(frame), exact_duplicates=len(frame)-len(clean),
                 conflicting_keys=0, missing_keys=0, natural_duplicates=0)
    identity={"source","patient_key","activity_code","event_start"}
    if identity <= set(clean):
        appointments=clean[clean.source.eq("appointment")].copy()
        rest=clean[~clean.source.eq("appointment")]
        if not appointments.empty:
            parts=appointments[["patient_key","activity_code","event_start"]].fillna("").astype(str)
            natural=parts.patient_key+"|"+parts.activity_code+"|"+parts.event_start
            if "machine" in appointments:
                natural=natural.where(parts.patient_key.ne(""),natural+"|"+appointments.machine.fillna(""))
            appointments["event_key"]="natural:"+natural
            semantic = [c for c in appointments if c not in {
                "source_rows", "run_id", "contract_version", "completion_candidates", "machine_inferred"}]
            unique=appointments.drop_duplicates(subset=semantic)
            audit["natural_duplicates"]=len(appointments)-len(unique)
            clean=pd.concat([rest,unique],ignore_index=True)
    if "event_key" not in clean:
        clean["event_key"] = None
    missing = clean.event_key.isna() | clean.event_key.eq("")
    audit["missing_keys"] = int(missing.sum())
    repeated = clean.loc[~missing, "event_key"].duplicated(keep=False)
    bad = set(clean.loc[~missing].loc[repeated, "event_key"])
    audit["conflicting_keys"] = len(bad)
    # Conflicting versions have no trustworthy ordering/winner in the export.
    return clean.loc[~clean.event_key.isin(bad)].copy(), audit


def slot_overlap(slot_start, slot_end, actual_start, actual_end):
    return max(0, min(slot_end, actual_end)-max(slot_start, actual_start))


def interval_stats(intervals):
    valid = sorted((float(a),float(b)) for a,b in intervals
                   if pd.notna(a) and pd.notna(b) and b > a)
    if not valid:
        return dict(window_minutes=None, occupied_minutes=None, free_minutes=None,
                    free_gt30_minutes=None, gap_eq30_count=0, gap_count=0,
                    gap_gt30_count=0, overlap_minutes=None, gaps=[],gap_intervals=[])
    merged = []
    for a,b in valid:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a,b])
    gaps = [b[0]-a[1] for a,b in zip(merged, merged[1:])]
    occupied = sum(b-a for a,b in merged)
    return dict(window_minutes=merged[-1][1]-merged[0][0],
                occupied_minutes=occupied, free_minutes=sum(gaps),
                free_gt30_minutes=sum(g for g in gaps if g > 30),
                gap_eq30_count=sum(math.isclose(g,30) for g in gaps),
                gap_count=len(gaps), gap_gt30_count=sum(g > 30 for g in gaps),
                overlap_minutes=sum(b-a for a,b in valid)-occupied, gaps=gaps,
                gap_intervals=[(a[1],b[0]) for a,b in zip(merged,merged[1:])])


def distribution(values, patients, minimum=5):
    values = np.asarray([v for v in values if pd.notna(v) and math.isfinite(float(v))], dtype=float)
    hidden = len(patients) < minimum or not len(values)
    out = dict(n=None if hidden else len(values), patients=None if hidden else len(patients),
               suppressed=hidden, low=None, q1=None, median=None, q3=None, high=None)
    if not hidden:
        q1,median,q3 = np.quantile(values, [0.25,0.5,0.75], method="linear")
        inside = values[(values >= q1-1.5*(q3-q1)) & (values <= q3+1.5*(q3-q1))]
        out.update(low=float(inside.min()), q1=float(q1), median=float(median),
                   q3=float(q3), high=float(inside.max()))
    return out


def status_group(value):
    status = str(value or "").strip().casefold()
    if any(s in status for s in ("cancel", "abgebroch", "storniert")):
        return "cancelled"
    if "delete" in status:
        return "deleted"
    if any(s in status for s in ("complet", "compltfinish", "manuell be", "abgeschlossen", "delivered")):
        return "completed"
    if status in {"open","pending","", "in progress", "scheduled", "offen"} or status.startswith(("in progress","inprogress","pending")):
        return "open"
    return "other"
