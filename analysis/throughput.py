from collections import defaultdict
import pandas as pd
from .metrics import deduplicate, status_group, slot_overlap, interval_stats, distribution, natural_key
from .gap_context import collect as collect_gap_context, publish as publish_gap_context

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
    rows["kind"] = profile.classify_activities(rows)
    relevant=rows.source.eq("delivery") | rows.kind.str.startswith("treatment")
    audit["unmapped_device_rows"]=int((relevant & ~rows.machine.isin(profile.machines)).sum())
    rows = rows[rows.machine.isin(profile.machines)].copy()
    # A calendar-only machine cannot establish technical utilization, even if
    # configured alongside R&V devices. Do not treat its slots as idle time.
    connected = set(rows.loc[rows.source.eq('delivery'), 'machine'])
    rows = rows[rows.machine.isin(connected)].copy()
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
    # Unknown labels may provide timing, but never establish treatment without R&V.
    # Preserve every declared candidate, even an ambiguous one; infer only a unique
    # one-to-one containment of a technical visit by a documented activity interval.
    inferred_candidates, inferred_reverse = defaultdict(list), defaultdict(list)
    unknown = rows[rows.source.eq('appointment') & rows.kind.eq('unknown') &
                   rows.status.isin(['completed','open']) & rows.patient_key.ne('')]
    for idx,a in unknown.iterrows():
        if any(pd.isna(a[col]) for col in ['event_start','event_end','activity_start','activity_end']):
            continue
        if (a.activity_start.date()!=a.activity_end.date() or a.event_start.date()!=a.event_end.date()
            or not 0 < (a.activity_end-a.activity_start).total_seconds()/60 <= profile.max_interval_minutes
            or not 0 < (a.event_end-a.event_start).total_seconds()/60 <= 480):
            continue
        for s in session_groups[(a.patient_key,a.machine,a.date)]:
            if candidate_by_visit.get(s['visit']):
                continue
            delta = (s['start']-a.event_start).total_seconds()/60
            if (-120 <= delta <= 240 and pd.notna(s['start']) and pd.notna(s['end'])
                and a.activity_start <= s['start'] < s['end'] <= a.activity_end):
                inferred_candidates[idx].append(s['visit'])
                inferred_reverse[s['visit']].append(idx)
    inferred = {idx:visits[0] for idx,visits in inferred_candidates.items()
                if len(visits)==1 and len(inferred_reverse[visits[0]])==1}
    audit['inferred_timing_slots'] = len(inferred)
    audit['ambiguous_inferred_timing_slots'] = len(inferred_candidates)-len(inferred)
    if inferred:
        appts = pd.concat([appts,unknown.loc[list(inferred)]])
        winners.update(inferred)
    appts['inferred_timing'] = appts.index.isin(inferred)
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
        # ActivityEndDateTime is a documented actual end, NOT ScheduledEndTime.
        workflow_end = a.activity_end if pd.notna(a.activity_end) else a.completed
        record("workflow",technical_start,workflow_end,base, pd.isna(a.activity_end))
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
    slot_columns = ["patient_key","machine","date","matched","inferred_timing"]
    slot_frame = appts[["patient_key","machine","date"]].copy()
    slot_frame["machine"] = slot_frame.machine.map(profile.machines)
    slot_frame["matched"] = [i in winners for i in appts.index]
    slot_frame["inferred_timing"] = appts.inferred_timing
    expected=defaultdict(int)
    for row in slot_frame.itertuples():
        if pd.notna(row.date):
            expected[(row.machine,row.date)]+=1
    for session in sessions:
        if session["visit"] not in consumed and pd.notna(session["date"]):
            expected[(profile.machines[session["machine"]],session["date"])]+=1
    blocks = rows[rows.source.eq("appointment") & rows.kind.eq("block") &
                  ~rows.status.isin(["cancelled","deleted"])].copy()
    activities = rows[rows.source.eq('appointment') & ~rows.status.isin(['cancelled','deleted'])].copy()
    return dict(visits=visits,slots=slot_frame[slot_columns],audit=audit,blocks=blocks,expected=expected,activities=activities)


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
                visible = set(df.groupby("machine").patient_key.nunique().loc[lambda n: n >= profile.minimum_patients].index)
                devices = set(df.machine)|{key[0] for key in expected}
                for machine in sorted(devices,key=natural_key)+["ALL"]:
                    group = df[df.machine.isin(visible)] if machine == "ALL" else df[df.machine.eq(machine)]
                    slot = prepared["slots"]
                    slot = slot[(slot.date >= max(profile.start,str(period.start_time.date()))) &
                                (slot.date <= min(profile.end,str(period.end_time.date())))]
                    if machine != "ALL":
                        slot = slot[slot.machine.eq(machine)]
                    else:
                        slot = slot[slot.machine.isin(visible)]
                    patients = set(group.patient_key)
                    suppressed = len(patients)<profile.minimum_patients
                    measured_slot_patients = set(group.loc[group.booked.notna(),"patient_key"])
                    safe_slots = len(measured_slot_patients)>=profile.minimum_patients
                    inferred_slot = slot[slot.get('inferred_timing',pd.Series(False,index=slot.index))]
                    inferred_count = (len(inferred_slot) if inferred_slot.empty or
                                      inferred_slot.patient_key.nunique() >= profile.minimum_patients else None)
                    days,cycles,changes = [],[],[]
                    complete_cycles,complete_changes = [],[]
                    complete_cycle_patients,complete_change_patients = set(),set()
                    change_patients=set()
                    gap_context = {}
                    cycle_patients=set()
                    expected_group={key:n for key,n in expected.items()
                                    if (key[0] in visible if machine=='ALL' else key[0]==machine)}
                    for (device,day),d in group.groupby(["machine","date"]):
                        complete = len(d)>=expected_group.get((device,day),len(d))
                        # Observed neighbours are a separate sample from complete-day idle time.
                        previous = None
                        for row in d.sort_values(["start","end"]).itertuples():
                            if previous and previous.patient_key != row.patient_key:
                                pair = (previous.patient_key,row.patient_key)
                                cadence = (row.start-previous.start).total_seconds()/60
                                turnover = (row.start-previous.end).total_seconds()/60
                                if cadence > 0:
                                    cycles.append(cadence)
                                    cycle_patients.update(pair)
                                    if complete:
                                        complete_cycles.append(cadence)
                                        complete_cycle_patients.update(pair)
                                if turnover >= 0:
                                    changes.append(turnover)
                                    change_patients.update(pair)
                                    if complete:
                                        complete_changes.append(turnover)
                                        complete_change_patients.update(pair)
                            previous = row
                        # A missing visit interval is unknown occupancy, not idle time.
                        if not complete:
                            continue
                        intervals = [(a.timestamp()/60,b.timestamp()/60) for a,b in zip(d.start,d.end)]
                        stats = interval_stats(intervals)
                        stats["patients"] = set(d.patient_key)
                        stats["machine"] = d.machine.iloc[0]
                        blocks=prepared["blocks"]
                        raw_machine=next((key for key,label in profile.machines.items() if label==d.machine.iloc[0]),None)
                        activities=prepared.get('activities',prepared['blocks'])
                        activities=activities[activities.machine.eq(raw_machine) & activities.date.eq(day)]
                        collect_gap_context(activities,stats['gap_intervals'],gap_context)
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
                    window = sum(d["window_minutes"] or 0 for d in days)
                    free = sum(d["free_minutes"] or 0 for d in days)
                    gt30 = sum(d["free_gt30_minutes"] or 0 for d in days)
                    free_patients=set().union(*(d['patients'] for d in days))
                    safe_free=len(free_patients)>=profile.minimum_patients
                    booked = group.booked.sum()
                    positioned = group[group.booked.notna()].copy()
                    if not {'slot_start','slot_end'}.issubset(positioned.columns):
                        positioned = positioned.iloc[:0]
                    else:
                        positioned = positioned[positioned.slot_start.notna() & positioned.slot_end.notna()]
                    safe_position = positioned.patient_key.nunique()>=profile.minimum_patients
                    inside = ((positioned.start>=positioned.slot_start) & (positioned.start<positioned.slot_end)) if safe_position else None
                    kpi = dict(visits=len(group),expected_visits=sum(expected_group.values()),
                               unique_patients=len(patients),device_days=len(days),
                               complete_device_days=len(days),incomplete_device_days=len(expected_group)-len(days),
                               measured_visits_pct=100*len(group)/sum(expected_group.values()) if expected_group else None,
                               relevant_slots=len(slot),matched_slots=int(slot.matched.sum()),
                               inferred_timing_slots=inferred_count,
                               match_pct=100*slot.matched.mean() if len(slot) else None,
                               measurable_slots=int(group.booked.notna().sum()),
                               slot_position_n=len(positioned) if safe_position else None,
                               slot_overlap_visits_pct=100*((positioned.start<positioned.slot_end) & (positioned.end>positioned.slot_start)).mean() if safe_position else None,
                               fully_in_slot_pct=100*(inside & (positioned.end<=positioned.slot_end)).mean() if safe_position else None,
                               booked_minutes=float(booked) if safe_slots else None,
                               overlap_minutes_in_slots=float(group.overlap.sum()) if safe_slots else None,
                               duration_minutes_in_slots=float(group.loc[group.booked.notna(),'duration'].sum()) if safe_slots else None,
                               slot_coverage_pct=100*group.overlap.sum()/booked if booked>0 and safe_slots else None,
                               duration_ratio_pct=100*group.loc[group.booked.notna(),"duration"].sum()/booked if booked>0 and safe_slots else None,
                               slotted_duration_mean=group.loc[group.booked.notna(),"duration"].mean() if safe_slots else None,
                               booked_mean=group.booked.mean() if safe_slots else None,
                               duration_mean=group.duration.mean(),fallback_intervals=int(group.fallback.sum()),
                               free_hours=free/60,free_gt30_hours=gt30/60,window_hours=window/60,
                               free_ge30_hours=sum(sum(y-x for x,y in d['gap_intervals'] if y-x>=30) for d in days)/60,
                               free_ge30_count=sum(sum(y-x>=30 for x,y in d['gap_intervals']) for d in days),
                               free_pct=100*free/window if window else None,
                               occupied_pct=100*(window-free)/window if window else None,
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
                            if key.startswith(('free_','window_','nominal_')) or key in {'exact30_gaps','overlap_minutes','occupied_pct'}:
                                kpi[key]=None
                    if suppressed:
                        kpi = {key:None for key in kpi}
                    else:
                        kpi = {key:(None if pd.isna(value) else float(value)) for key,value in kpi.items()}
                    group_distributions = {
                        "duration":distribution(group.duration,patients,profile.minimum_patients),
                        "booked":distribution(group.booked,measured_slot_patients,profile.minimum_patients),
                        "slot_coverage":distribution(100*group.overlap/group.booked,measured_slot_patients,profile.minimum_patients),
                        "duration_ratio":distribution(100*group.duration/group.booked,measured_slot_patients,profile.minimum_patients),
                        "cycle":distribution(cycles,cycle_patients,profile.minimum_patients),
                        "change":distribution(changes,change_patients,profile.minimum_patients),
                        "cycle_complete_days":distribution(complete_cycles,complete_cycle_patients,profile.minimum_patients),
                        "change_complete_days":distribution(complete_changes,complete_change_patients,profile.minimum_patients),
                        "free":distribution([d["free_minutes"]/60 for d in days],free_patients,profile.minimum_patients),
                        "free_gt30":distribution([d["free_gt30_minutes"]/60 for d in days],free_patients,profile.minimum_patients),
                        "free_pct":distribution([100*d["free_minutes"]/d["window_minutes"] for d in days if d["window_minutes"]],free_patients,profile.minimum_patients),
                        "occupied_pct":distribution([100*d["occupied_minutes"]/d["window_minutes"] for d in days if d["window_minutes"]],free_patients,profile.minimum_patients),
                        "free_gt30_pct":distribution([100*d["free_gt30_minutes"]/d["window_minutes"] for d in days if d["window_minutes"]],free_patients,profile.minimum_patients),
                    }
                    groups.append(dict(machine=machine,suppressed=suppressed,kpi=kpi,distributions=group_distributions,
                                       transition_scope='consecutive_observed_visits',
                                       gap_activities=publish_gap_context(gap_context,profile.minimum_patients,safe_free and not suppressed),
                                       pool_excludes_suppressed=machine=="ALL" and bool(devices-visible)))
                result[granularity][model].append(dict(
                    label=str(period),start=str(period.start_time.date()),end=str(period.end_time.date()),
                    partial=str(period.start_time.date())<profile.start or str(period.end_time.date())>profile.end,
                    groups=groups))
    return result
