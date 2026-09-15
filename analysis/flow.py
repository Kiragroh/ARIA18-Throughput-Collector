"""All-modality treatment and counselling chains, with explicit censoring."""
from collections import defaultdict
import pandas as pd
from .metrics import deduplicate, status_group


def summarize(events, profile, *, data_through, context_start, sources_complete=False):
    events, audit = deduplicate(events)
    out = dict(completed_counselling_appointments=0, open_counselling_appointments=0,
               other_counselling_appointments=0,
               cancelled_counselling_appointments=0, registered_counselling_appointments=0,
               counselling_episodes=0, mature_episodes=0, matched_mature=0,
               observation_mature=0, unresolved_mature=0, provisional=0,
               multiple_counselling=0, treatment_episodes=0, completed_treatment_episodes=0,
               open_with_treatment=0, cancelled_with_later_contact=0,
               unmatched_treatment_episodes=0, left_boundary_chains=0,
               unresolved_pct=None, cancellation_pct=None, sources_complete=bool(sources_complete),
               duplicates=audit, series=[])
    if events.empty:
        return out
    start, end = pd.Timestamp(profile.start), pd.Timestamp(profile.end)+pd.Timedelta(days=1)
    through = pd.Timestamp(data_through) if data_through else pd.NaT
    context = pd.Timestamp(context_start) if context_start else pd.NaT
    events["event_start"] = pd.to_datetime(events.event_start, errors="coerce",format="mixed")
    events["event_end"] = pd.to_datetime(events.event_end, errors="coerce",format="mixed").fillna(events.event_start)
    events["status"] = events.status.map(profile.classify_status)
    # Future appointments can document observation, but never delivered treatment.
    tx = events[events.kind.str.startswith("treatment") & events.status.eq("completed")]
    tx = tx[tx.event_start <= through + pd.Timedelta(days=1)-pd.Timedelta(microseconds=1)] if pd.notna(through) else tx.iloc[0:0]
    episodes = defaultdict(list)
    for patient, group in tx.groupby("patient_key"):
        for row in group.sort_values("event_start").itertuples():
            a,b = row.event_start, row.event_end
            if pd.isna(a) or b < a:
                continue
            existing = episodes[patient]
            if existing and a.normalize() <= existing[-1][1].normalize()+pd.Timedelta(days=30):
                existing[-1][1] = max(existing[-1][1],b)
            else:
                existing.append([a,b])
    daily = defaultdict(lambda: defaultdict(int))
    for eps in episodes.values():
        for a,b in eps:
            if start <= a < end:
                out["treatment_episodes"] += 1
                daily[str(a.date())]["treatment_starts"] += 1
            # A quiet 30-day interval must be observed beyond the last delivery.
            if start <= b < end and pd.notna(through) and b.normalize()+pd.Timedelta(days=30) <= through:
                out["completed_treatment_episodes"] += 1
                daily[str(b.date())]["treatment_ends"] += 1
    matched_episode_keys = set()
    for patient, group in events.groupby("patient_key"):
        eps = episodes[patient]
        consults = group[group.kind.eq("counselling") & ~group.status.eq("deleted")].sort_values("event_start")
        chains = defaultdict(list)
        for row in consults.itertuples():
            t = row.event_start
            if pd.isna(t):
                continue
            if start <= t < end:
                out["registered_counselling_appointments"] += 1
                col = {"completed":"completed_counselling_appointments",
                       "open":"open_counselling_appointments","cancelled":"cancelled_counselling_appointments",
                       "other":"other_counselling_appointments"}.get(row.status)
                if col:
                    out[col] += 1
                if row.status == "cancelled":
                    later = group[(group.event_start > t) &
                                  group.kind.isin(["counselling","observation"]) &
                                  ~group.status.isin(["cancelled","deleted"])]
                    out["cancelled_with_later_contact"] += int(not later.empty)
            if row.status in {"cancelled","other"}:
                continue
            # A consultation during an active episode cannot retroactively match its start.
            next_index = next((i for i,(a,b) in enumerate(eps) if a >= t), None)
            previous_index = max((i for i,(a,b) in enumerate(eps) if b < t), default=-1)
            key = ("next",next_index) if next_index is not None else ("unmatched",previous_index)
            chains[key].append(row)
        for key, rows in chains.items():
            completed = [r for r in rows if r.status == "completed"]
            next_episode = eps[key[1]] if key[0] == "next" else None
            # Completed visits define the primary cohort; inferred open visits are separate.
            out["open_with_treatment"] += sum(start <= r.event_start < end and r.status == "open"
                                               for r in rows) if next_episode else 0
            if not completed:
                continue
            first, last = completed[0].event_start, completed[-1].event_start
            if next_episode:
                matched_episode_keys.add((patient,key[1]))
            if not start <= first < end:
                continue
            out["counselling_episodes"] += 1
            out["multiple_counselling"] += int(len(completed) > 1)
            daily[str(first.date())]["counselling_episodes"] += 1
            left = pd.isna(context) or first.normalize() < context+pd.Timedelta(days=30)
            out["left_boundary_chains"] += int(left)
            mature = pd.notna(through) and last.normalize()+pd.DateOffset(months=3) <= through and not left
            if not mature:
                out["provisional"] += 1
                continue
            out["mature_episodes"] += 1
            observation = group[group.kind.eq("observation") &
                                (group.event_start > last) &
                                ~group.status.isin(["cancelled","deleted"])]
            if next_episode:
                out["matched_mature"] += 1
            elif not observation.empty:
                out["observation_mature"] += 1
            else:
                out["unresolved_mature"] += 1
    out["unmatched_treatment_episodes"] = sum(start <= a < end and (p,i) not in matched_episode_keys
                                              for p,eps in episodes.items() for i,(a,b) in enumerate(eps))
    if out["mature_episodes"] and sources_complete:
        out["unresolved_pct"] = 100*out["unresolved_mature"]/out["mature_episodes"]
    if out["registered_counselling_appointments"]:
        out["cancellation_pct"] = 100*out["cancelled_counselling_appointments"]/out["registered_counselling_appointments"]
    out["series"] = [dict(date=day, **dict(values)) for day,values in sorted(daily.items())]
    return out
