"""Local clinical counting. Only aggregate output may leave this module."""
import pandas as pd
from .metrics import deduplicate, natural_key
from .ingest import normalize_flow, resolve_treatment_devices


def treatment_days(events, profile, data_through):
    rows, _ = deduplicate(normalize_flow(resolve_treatment_devices(events, profile), profile))
    for col in ("machine", "plan_key", "course_key", "patient_key"):
        if col not in rows:
            rows[col] = ""
        rows[col] = rows[col].fillna("").astype(str)
    rows["event_start"] = pd.to_datetime(rows.event_start, errors="coerce", format="mixed")
    rows["event_end"] = pd.to_datetime(rows.event_end, errors="coerce", format="mixed").fillna(rows.event_start)
    rows["date"] = rows.event_start.dt.strftime("%Y-%m-%d")
    rows["status"] = rows.status.map(profile.classify_status)
    rows = rows[rows.kind.str.startswith("treatment") & rows.status.eq("completed")
                & rows.patient_key.ne("") & (rows.event_start < pd.Timestamp(data_through)+pd.Timedelta(days=1))].copy()
    rows["raw_machine"] = rows.machine
    rows["machine"] = rows.raw_machine.map(profile.machines).fillna(
        rows.kind.map(profile.manual_machine_labels)).fillna("Nicht zugeordnet")
    technical = rows[rows.source.eq("delivery")].copy()
    if "fraction" not in technical:
        technical["fraction"] = None
    technical["fraction"] = pd.to_numeric(technical.fraction, errors="coerce")
    # Field rows are one delivered plan-fraction, not separate treatments.
    keys = ["patient_key", "plan_key", "machine", "date", "fraction"]
    technical = technical.sort_values("event_start").drop_duplicates(keys)
    technical["evidence"] = "technical"
    linked = set(zip(technical.patient_key, technical.machine, technical.date))
    manual = rows[rows.source.eq("appointment")].copy()
    manual = manual.loc[[key not in linked for key in zip(manual.patient_key, manual.machine, manual.date)]]
    manual["evidence"] = "manual"
    manual["fraction"] = None
    result = pd.concat([technical.astype(object), manual.astype(object)], ignore_index=True).infer_objects(copy=False)
    result["fraction_countable"] = result.evidence.eq("manual") | (
        result.plan_key.ne("") & pd.to_numeric(result.fraction, errors="coerce").fillna(0).gt(0))
    return result


def plan_courses(days, data_through):
    """Plan starts need delivery evidence; silence is an inferred end, not completion."""
    output = []
    through = pd.Timestamp(data_through).normalize()
    technical = days[days.evidence.eq("technical") & days.plan_key.ne("")]
    for (patient, plan), group in technical.groupby(["patient_key", "plan_key"]):
        group = group.sort_values("event_start")
        first, last = group.event_start.min(), group.event_end.max()
        source_first = pd.to_datetime(group.get("plan_first_treatment", pd.Series(dtype=object)),
                                      errors="coerce", format="mixed").min()
        if pd.notna(source_first):
            first = min(first, source_first)
        target = pd.to_numeric(group.get("planned_fractions", pd.Series(dtype=float)), errors="coerce")
        target = target[target.gt(0)].dropna().unique()
        planned = float(target[0]) if len(target) == 1 else None
        fractions = group.loc[group.fraction_countable, "fraction"].nunique()
        starts_with_first = bool((group.loc[group.event_start.eq(group.event_start.min()),"fraction"] == 1).any())
        # Fragmentary left context must not count as a fully delivered plan.
        complete = planned is not None and fractions >= planned
        left_truncated = (pd.notna(source_first) and source_first.normalize() < group.event_start.min().normalize()
                          or not starts_with_first and pd.isna(source_first))
        observed_silence = (through-last.normalize()).days > 7
        state = "completed" if complete else (
            "ended_incomplete" if observed_silence and planned is not None and not left_truncated else
            "ended_target_unknown" if observed_silence else "open_followup")
        dates = group.event_start.dt.normalize().drop_duplicates().sort_values()
        output.append(dict(patient_key=patient, plan_key=plan, course_key=group.course_key.iloc[0],
                           machine=group.machine.iloc[0], start=first, last=last,
                           end=last if state != "open_followup" else pd.NaT,
                           state=state, fractions=fractions, planned_fractions=planned,
                           start_confirmed=bool(starts_with_first or pd.notna(source_first)),
                           resumed_after_gap=bool((dates.diff().dt.days > 7).any())))
    return pd.DataFrame(output, columns=["patient_key", "plan_key", "course_key", "machine", "start",
        "last", "end", "state", "fractions", "planned_fractions", "start_confirmed", "resumed_after_gap"])


def _cell(value, patients, minimum):
    return int(value) if value == 0 or len(set(patients)) >= minimum else None


def period_counts(days, plans, profile, start, end):
    current = days[days.date.between(start, end)]
    active = plans[plans.plan_key.isin(current.plan_key)]
    begun = plans[(plans.start >= pd.Timestamp(start)) & (plans.start < pd.Timestamp(end)+pd.Timedelta(days=1))
                  & plans.start_confirmed]
    if current.empty:
        return dict(patients=0, fractions=0, technical_fractions=0, manual_fractions=0,
                    treated_plans=0, new_plans=0, treatment_days=0, patients_per_day=None,
                    fractions_per_day=None, plan_ends_incomplete=0, plan_ends_complete=0,
                    plan_ends_target_unknown=0, plan_open_followup=0, plans_resumed_after_gap=0)
    n = profile.minimum_patients
    patients = current.patient_key
    valid = current[current.fraction_countable]
    technical = valid[valid.evidence.eq("technical")]
    manual = valid[valid.evidence.eq("manual")]
    ended = plans[plans.end.notna() & (plans.end >= pd.Timestamp(start))
                  & (plans.end < pd.Timestamp(end)+pd.Timedelta(days=1))]
    summary = dict(
        patients=_cell(patients.nunique(), patients, n),
        fractions=_cell(len(valid), valid.patient_key, n),
        technical_fractions=_cell(len(technical), technical.patient_key, n),
        manual_fractions=_cell(len(manual), manual.patient_key, n),
        treated_plans=_cell(len(active), active.patient_key, n),
        new_plans=_cell(len(begun), begun.patient_key, n),
        treatment_days=_cell(current.date.nunique(), patients, n),
        patients_per_day=float(current.groupby("date").patient_key.nunique().mean()) if patients.nunique() >= n else None,
        fractions_per_day=float(valid.groupby("date").size().reindex(current.date.unique(), fill_value=0).mean()) if valid.patient_key.nunique() >= n else None,
    )
    for state, name in [("completed", "plan_ends_complete"), ("ended_incomplete", "plan_ends_incomplete"),
                        ("ended_target_unknown", "plan_ends_target_unknown")]:
        subset = ended[ended.state.eq(state)]
        summary[name] = _cell(len(subset), subset.patient_key, n)
    pending = active[active.state.eq("open_followup")]
    summary["plan_open_followup"] = _cell(len(pending), pending.patient_key, n)
    resumed = active[active.resumed_after_gap]
    summary["plans_resumed_after_gap"] = _cell(len(resumed), resumed.patient_key, n)
    # Do not reveal a hidden evidence subgroup by subtraction.
    if summary["technical_fractions"] is None or summary["manual_fractions"] is None:
        summary["fractions"] = None
    return summary


def summarize_population(events, profile, metadata):
    days = treatment_days(events, profile, metadata["data_through"])
    plans = plan_courses(days, metadata["data_through"])
    comparison = str(metadata.get("comparison_population_complete", "")).lower() in {"1", "true", "1.0"}
    comparison = comparison and pd.Timestamp(metadata["context_start"]) <= pd.Timestamp(profile.start)-pd.DateOffset(years=1)
    result = dict(summary=period_counts(days, plans, profile, profile.start, profile.end),
                  comparison_available=comparison, periods={}, devices=[])
    for name in sorted(days.machine.unique(), key=natural_key):
        subset = days[days.machine.eq(name)]
        current = subset[subset.date.between(profile.start, profile.end)]
        if current.empty:
            continue
        counts = period_counts(subset, plans[plans.machine.eq(name)], profile, profile.start, profile.end)
        result["devices"].append(dict(machine=name, **counts,
            first_day=current.date.min() if current.patient_key.nunique() >= profile.minimum_patients else None,
            last_day=current.date.max() if current.patient_key.nunique() >= profile.minimum_patients else None))
    for granularity, freq in [("week", "W-SUN"), ("month", "M"), ("quarter", "Q"), ("year", "Y")]:
        rows = []
        for period in pd.period_range(profile.start, profile.end, freq=freq):
            a = max(profile.start, str(period.start_time.date()))
            b = min(profile.end, str(period.end_time.date()))
            prev_a = str((pd.Timestamp(a)-pd.DateOffset(years=1)).date())
            prev_b = str((pd.Timestamp(b)-pd.DateOffset(years=1)).date())
            rows.append(dict(label=str(period), start=a, end=b,
                current=period_counts(days, plans, profile, a, b),
                previous=period_counts(days, plans, profile, prev_a, prev_b) if comparison else None,
                devices=[dict(machine=name, **period_counts(days[days.machine.eq(name)],
                            plans[plans.machine.eq(name)], profile, a, b))
                         for name in sorted(days[days.date.between(a,b)].machine.unique(), key=natural_key)]))
        result["periods"][granularity] = rows
    result["quality"] = dict(
        technical_rows_without_fraction=int((days.evidence.eq("technical") & ~days.fraction_countable).sum()),
        plans_without_confirmed_start=int((~plans.start_confirmed).sum()),
        plans_without_target=int(plans.planned_fractions.isna().sum()))
    return result
