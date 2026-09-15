from collections import defaultdict
import pandas as pd
from .metrics import deduplicate, status_group, slot_overlap, interval_stats, distribution, natural_key

MODELS = ("activity","workflow","technical")
TIME_COLUMNS = ("event_start","event_end","activity_start","activity_end","completed")


def prepare_visits(events, profile):
    rows, audit = deduplicate(events)
    for col in TIME_COLUMNS:
        times = pd.to_datetime(rows.get(col, pd.Series(dtype="object")), errors="coerce",format="mixed")
        rows[col] = (times.dt.tz_convert(profile.timezone) if isinstance(times.dtype,pd.DatetimeTZDtype)
                     else times.dt.tz_localize(profile.timezone,ambiguous="NaT",nonexistent="NaT"))
    for col in ("patient_key","machine","plan_key","course_key","activity_code","source","status"):
        if col not in rows:
            rows[col] = ""
        rows[col] = rows[col].fillna("").astype(str)
    if "fraction" not in rows:
        rows["fraction"] = 0
    rows["fraction"] = rows.fraction.fillna(0)
    rows["status"] = rows.status.map(profile.classify_status)
    rows["date"] = rows.event_start.dt.strftime("%Y-%m-%d")
    rows["kind"] = rows.activity_code.map(profile.activity_codes).fillna("unknown")
    relevant=rows.source.eq("delivery") | rows.kind.str.startswith("treatment")
    audit["unmapped_device_rows"]=int((relevant & ~rows.machine.isin(profile.machines)).sum())
    rows = rows[rows.machine.isin(profile.machines)].copy()
    technical = rows[rows.source.eq("delivery") & rows.patient_key.ne("")]
    incomplete = technical.plan_key.eq("") | pd.to_numeric(technical.fraction,errors="coerce").fillna(0).le(0)
    audit["technical_identity_incomplete_rows"] = int(incomplete.sum())
    technical = technical[~incomplete]
    images = rows[rows.source.eq("imaging")]
    image_groups = {key:g for key,g in images.groupby(["patient_key","machine","date","plan_key","fraction"],dropna=False)}
    plans = []
    keys = ["patient_key","machine","date","plan_key","fraction"]
    for key,group in technical.groupby(keys,dropna=False):
        beam, finish = group.event_start.min(),group.event_end.max()
        image = image_groups.get(key)
        candidate = pd.NaT
        if image is not None:
            allowed = image[(image.event_start <= beam) &
                            (image.event_start >= beam-pd.Timedelta(minutes=profile.imaging_before_beam_minutes))]
            candidate = allowed.event_start.min()
        clinical = candidate if pd.notna(candidate) else beam
        plans.append(dict(patient_key=key[0],machine=key[1],date=key[2],start=clinical,
                          end=finish,beam=beam,imaging=pd.notna(candidate),plan_count=1))
    plan_frame = pd.DataFrame(plans)
    sessions = []
    if not plan_frame.empty:
        for key,group in plan_frame.groupby(["patient_key","machine","date"]):
            merged = []
            for row in group.sort_values("start").to_dict("records"):
                if merged and row["start"] <= merged[-1]["end"]+pd.Timedelta(minutes=profile.visit_merge_minutes):
                    merged[-1]["end"] = max(merged[-1]["end"],row["end"])
                    merged[-1]["plan_count"] += row["plan_count"]
                    merged[-1]["imaging"] |= row["imaging"]
                else:
                    merged.append(row.copy())
            sessions.extend(merged)
    for i,row in enumerate(sessions):
        row["visit"] = i
    appts = rows[rows.source.eq("appointment") & rows.kind.str.startswith("treatment") &
                 ~rows.status.isin(["cancelled","deleted"]) & rows.patient_key.ne("")].copy()
    # Match at visit level, not plan level. Keep every unmatched slot in its denominator.
    candidate_by_appt, candidate_by_visit = defaultdict(list),defaultdict(list)
    session_groups = defaultdict(list)
    for session in sessions:
        session_groups[(session["patient_key"],session["machine"],session["date"])].append(session)
    for idx,a in appts.iterrows():
        for s in session_groups[(a.patient_key,a.machine,a.date)]:
            delta = (s["start"]-a.event_start).total_seconds()/60
            if -120 <= delta <= 240:
                candidate_by_appt[idx].append((abs(delta),s["visit"]))
                candidate_by_visit[s["visit"]].append((abs(delta),idx))
    winners = {}
    ambiguous = 0
    for idx,candidates in candidate_by_appt.items():
        ordered = sorted(candidates)
        if len(ordered)>1 and ordered[0][0] == ordered[1][0]:
            ambiguous += 1
            continue
        delta,visit = ordered[0]
        reverse = sorted(candidate_by_visit[visit])
        if reverse[0][1] == idx and (len(reverse)==1 or reverse[0][0] < reverse[1][0]):
            winners[idx] = visit
    audit.update(relevant_slots=len(appts),matched_slots=len(winners),ambiguous_matches=ambiguous,
                 technical_plan_fractions=len(plans),technical_visits=len(sessions),
                 multiple_plan_visits=sum(s["plan_count"]>1 for s in sessions))
    audit["slots_missing_calendar_end"]=int(appts.event_end.isna().sum())
    audit["slots_missing_activity_start"]=int(appts.activity_start.isna().sum())
    audit["slots_missing_activity_end"]=int(appts.activity_end.isna().sum())
    audit["slots_missing_completion_history"]=int(appts.completed.isna().sum())
    output = {model:[] for model in MODELS}
    consumed = set(winners.values())

    def record(model, start, end, base, fallback=False):
        if pd.isna(start) or pd.isna(end):
            return
        duration = (end-start).total_seconds()/60
        if duration <= 0 or duration > profile.max_interval_minutes or start.date()!=end.date():
            audit[model+"_invalid_intervals"] = audit.get(model+"_invalid_intervals",0)+1
            return
        overlap,booked = None,None
        if pd.notna(base["slot_start"]) and pd.notna(base["slot_end"]):
            booked = (base["slot_end"]-base["slot_start"]).total_seconds()/60
            if not 0 < booked <= 480:
                booked = None
            else:
                overlap = max(0,(min(end,base["slot_end"])-max(start,base["slot_start"])).total_seconds()/60)
        output[model].append(dict(**base,start=start,end=end,duration=duration,
                                  booked=booked,overlap=overlap,fallback=int(fallback)))

    for idx,a in appts.iterrows():
        s = sessions[winners[idx]] if idx in winners else None
        base = dict(patient_key=a.patient_key,machine=profile.machines[a.machine],date=a.date,
                    slot_start=a.event_start,slot_end=a.event_end,matched=s is not None)
        technical_start,technical_end = (s["start"],s["end"]) if s else (pd.NaT,pd.NaT)
        # Do not silently substitute a booked slot for a measured interval.
        act_start = a.activity_start if pd.notna(a.activity_start) else technical_start
        act_end = a.activity_end if pd.notna(a.activity_end) else technical_end
        record("activity",act_start,act_end,base,
               pd.isna(a.activity_start) or pd.isna(a.activity_end))
        record("workflow",technical_start,a.completed,base)
        record("technical",technical_start,technical_end,base)
    for s in sessions:
        if s["visit"] in consumed:
            continue
        base = dict(patient_key=s["patient_key"],machine=profile.machines[s["machine"]],
                    date=s["date"],slot_start=pd.NaT,slot_end=pd.NaT,matched=False)
        record("technical",s["start"],s["end"],base)
        record("activity",s["start"],s["end"],base,True)
    columns = ["patient_key","machine","date","slot_start","slot_end","matched","start","end",
               "duration","booked","overlap","fallback"]
    visits = {model:pd.DataFrame(items,columns=columns) for model,items in output.items()}
    slot_columns = ["patient_key","machine","date","matched"]
    slot_frame = appts[["patient_key","machine","date"]].copy()
    slot_frame["machine"] = slot_frame.machine.map(profile.machines)
    slot_frame["matched"] = [i in winners for i in appts.index]
    expected=defaultdict(int)
    for row in slot_frame.itertuples():
        if pd.notna(row.date):
            expected[(row.machine,row.date)]+=1
    for session in sessions:
        if session["visit"] not in consumed and pd.notna(session["date"]):
            expected[(profile.machines[session["machine"]],session["date"])]+=1
    blocks = rows[rows.source.eq("appointment") & rows.kind.eq("block") &
                  ~rows.status.isin(["cancelled","deleted"])].copy()
    return dict(visits=visits,slots=slot_frame[slot_columns],audit=audit,blocks=blocks,expected=expected)


def _bucket(date, granularity):
    return pd.Timestamp(date).to_period({"week":"W-SUN","month":"M","quarter":"Q","year":"Y"}[granularity])


def aggregate(prepared, profile):
    result = {}
    for granularity in ("week","month","quarter","year"):
        start, end = _bucket(profile.start,granularity),_bucket(profile.end,granularity)
        result[granularity] = {}
        for model,frame in prepared["visits"].items():
            result[granularity][model] = []
            for period in pd.period_range(start,end,freq=start.freq):
                groups = []
                df = frame[(frame.date >= max(profile.start,str(period.start_time.date()))) &
                           (frame.date <= min(profile.end,str(period.end_time.date())))]
                expected={key:n for key,n in prepared["expected"].items()
                          if max(profile.start,str(period.start_time.date()))<=key[1]<=min(profile.end,str(period.end_time.date()))}
                for machine in sorted(set(df.machine)|{key[0] for key in expected},key=natural_key)+["ALL"]:
                    group = df if machine == "ALL" else df[df.machine.eq(machine)]
                    slot = prepared["slots"]
                    slot = slot[(slot.date >= max(profile.start,str(period.start_time.date()))) &
                                (slot.date <= min(profile.end,str(period.end_time.date())))]
                    if machine != "ALL":
                        slot = slot[slot.machine.eq(machine)]
                    patients = set(group.patient_key)
                    suppressed = len(patients)<profile.minimum_patients
                    measured_slot_patients = set(group.loc[group.booked.notna(),"patient_key"])
                    safe_slots = len(measured_slot_patients)>=profile.minimum_patients
                    days,cycles,changes = [],[],[]
                    cycle_patients=set()
                    expected_group={key:n for key,n in expected.items() if machine=='ALL' or key[0]==machine}
                    for (device,day),d in group.groupby(["machine","date"]):
                        # A missing visit interval is unknown occupancy, not idle time.
                        if len(d)<expected_group.get((device,day),len(d)):
                            continue
                        intervals = [(a.timestamp()/60,b.timestamp()/60) for a,b in zip(d.start,d.end)]
                        stats = interval_stats(intervals)
                        stats["patients"] = set(d.patient_key)
                        stats["machine"] = d.machine.iloc[0]
                        blocks=prepared["blocks"]
                        raw_machine=next((key for key,label in profile.machines.items() if label==d.machine.iloc[0]),None)
                        blocks=blocks[blocks.machine.eq(raw_machine) & blocks.date.eq(day)]
                        blocked_gaps=[]
                        for block in blocks.itertuples():
                            if pd.isna(block.event_start) or pd.isna(block.event_end):
                                continue
                            a,b=block.event_start.timestamp()/60,block.event_end.timestamp()/60
                            for g1,g2 in stats["gap_intervals"]:
                                if min(b,g2)>max(a,g1):
                                    blocked_gaps.append((max(a,g1),min(b,g2)))
                        stats["blocked_free_minutes"]=interval_stats(blocked_gaps)["occupied_minutes"] or 0
                        stats["nominal_hours"]=profile.opening_hours.get(raw_machine) if profile.opening_hours_confirmed else None
                        days.append(stats)
                        ordered = d.sort_values(["start","end"])
                        max_end = None
                        previous = None
                        for row in ordered.itertuples():
                            if previous and previous.patient_key != row.patient_key:
                                cycle_patients.update((previous.patient_key,row.patient_key))
                                cycles.append((row.start-previous.start).total_seconds()/60)
                                changes.append(max(0,(row.start-max_end).total_seconds()/60))
                            previous = row
                            max_end = row.end if max_end is None else max(max_end,row.end)
                    window = sum(d["window_minutes"] or 0 for d in days)
                    free = sum(d["free_minutes"] or 0 for d in days)
                    gt30 = sum(d["free_gt30_minutes"] or 0 for d in days)
                    free_patients=set().union(*(d['patients'] for d in days))
                    safe_free=len(free_patients)>=profile.minimum_patients
                    booked = group.booked.sum()
                    kpi = dict(visits=len(group),unique_patients=len(patients),device_days=len(days),
                               complete_device_days=len(days),incomplete_device_days=len(expected_group)-len(days),
                               measured_visits_pct=100*len(group)/sum(expected_group.values()) if expected_group else None,
                               relevant_slots=len(slot),matched_slots=int(slot.matched.sum()),
                               match_pct=100*slot.matched.mean() if len(slot) else None,
                               measurable_slots=int(group.booked.notna().sum()),
                               slot_coverage_pct=100*group.overlap.sum()/booked if booked>0 and safe_slots else None,
                               booked_mean=group.booked.mean() if safe_slots else None,
                               duration_mean=group.duration.mean(),fallback_intervals=int(group.fallback.sum()),
                               free_hours=free/60,free_gt30_hours=gt30/60,window_hours=window/60,
                               free_pct=100*free/window if window else None,
                               free_gt30_pct=100*gt30/window if window else None,
                               free_mean_hours=free/60/len(days) if days else None,
                               free_gt30_mean_hours=gt30/60/len(days) if days else None,
                               window_mean_hours=window/60/len(days) if days else None,
                               overlap_minutes=sum(d["overlap_minutes"] or 0 for d in days),
                               exact30_gaps=sum(d["gap_eq30_count"] for d in days),
                               free_in_documented_blocks_hours=sum(d["blocked_free_minutes"] for d in days)/60,
                               free_outside_documented_blocks_hours=(free-sum(d["blocked_free_minutes"] for d in days))/60,
                               nominal_hours_active_days=sum(d["nominal_hours"] for d in days)
                                if days and all(d["nominal_hours"] is not None for d in days) else None)
                    if not safe_free:
                        for key in kpi:
                            if key.startswith(('free_','window_','nominal_')) or key in {'exact30_gaps','overlap_minutes'}:
                                kpi[key]=None
                    if suppressed:
                        kpi = {key:None for key in kpi}
                    else:
                        kpi = {key:(None if pd.isna(value) else float(value)) for key,value in kpi.items()}
                    group_distributions = {
                        "duration":distribution(group.duration,patients,profile.minimum_patients),
                        "booked":distribution(group.booked,measured_slot_patients,profile.minimum_patients),
                        "slot_coverage":distribution(100*group.overlap/group.booked,measured_slot_patients,profile.minimum_patients),
                        "cycle":distribution(cycles,cycle_patients,profile.minimum_patients),
                        "change":distribution(changes,cycle_patients,profile.minimum_patients),
                        "free":distribution([d["free_minutes"]/60 for d in days],free_patients,profile.minimum_patients),
                        "free_gt30":distribution([d["free_gt30_minutes"]/60 for d in days],free_patients,profile.minimum_patients),
                        "free_pct":distribution([100*d["free_minutes"]/d["window_minutes"] for d in days if d["window_minutes"]],free_patients,profile.minimum_patients),
                        "free_gt30_pct":distribution([100*d["free_gt30_minutes"]/d["window_minutes"] for d in days if d["window_minutes"]],free_patients,profile.minimum_patients),
                    }
                    groups.append(dict(machine=machine,suppressed=suppressed,kpi=kpi,distributions=group_distributions))
                # Complementary suppression prevents deriving a small device via the pooled total.
                if any(g["suppressed"] for g in groups if g["machine"]!="ALL"):
                    groups[-1]["kpi"] = {k:None for k in groups[-1]["kpi"]}
                    groups[-1]["distributions"] = {k:distribution([],set(),profile.minimum_patients)
                                                   for k in groups[-1]["distributions"]}
                    groups[-1]["suppressed"] = True
                result[granularity][model].append(dict(
                    label=str(period),start=str(period.start_time.date()),end=str(period.end_time.date()),
                    partial=str(period.start_time.date())<profile.start or str(period.end_time.date())>profile.end,
                    groups=groups))
    return result
