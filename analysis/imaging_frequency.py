"""Image-object frequencies and descriptive, unadjusted visit associations."""
import pandas as pd
from .metrics import deduplicate, distribution, natural_key

KINDS = {"kv_cbct", "mv_cbct", "cbct_unknown", "exactrac_2d", "kv_2d", "mv_2d", "unknown_2d", "unknown"}


def equipment_for(profile, machine, day):
    for item in profile.equipment_periods:
        if item["machine"] == machine and item["start"] <= day <= item["end"]:
            return item
    return {}


def equipment_label(item):
    return (str(item.get("model", "Unbekannt")) + " / " + str(item.get("cbct_system", "unbekannt"))
            + (" (bestaetigt)" if item.get("confirmed") else " (unbestaetigt)")
            + (" | " + item["start"] + " bis " + item["end"] if item else ""))


def summarize_images(events, prepared, profile, metadata):
    available = metadata.get("image_objects_state") == "AVAILABLE"
    result = dict(available=available, source="DWH.FactPatientImage",
        classification="Bildnamen/-typen, keine verifizierte DICOM-Akquisitionsklassifikation",
        association="Eindeutiger messbarer Besuch derselben Person am selben Geraet und Kalendertag",
        acquisition_source=metadata.get('image_acquisition_state', 'NOT_INCLUDED'), periods={})
    if not available:
        return result
    images, _ = deduplicate(events[events.source.eq("image_object")])
    if images.empty:
        return result
    images = images.copy()
    images["date"] = pd.to_datetime(images.event_start, errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")
    images = images[images.date.between(profile.start, profile.end) & ~images.image_kind.isin(['reference','component'])].copy()
    images["image_kind"] = images.image_kind.where(images.image_kind.isin(KINDS), "unknown")
    images["seconds"] = pd.to_numeric(images.image_seconds, errors="coerce")
    images["seconds"] = images.seconds.where(images.seconds.gt(0) & images.seconds.le(3600))
    equipment = [equipment_for(profile, str(m), d) for m,d in zip(images.machine, images.date)]
    for i, item in zip(images.index, equipment):
        if images.at[i,"image_kind"] == "cbct_unknown" and item.get("confirmed") and item.get("cbct_modality") in {"kv","mv"}:
            images.at[i,"image_kind"] = item["cbct_modality"] + "_cbct"
    images["equipment"] = [equipment_label(e) for e in equipment]
    images['raw_machine'] = images.machine.fillna('').astype(str).str.strip()
    images['therapy_device'] = images.raw_machine.isin(profile.machines)
    images["machine"] = images.raw_machine.map(profile.machines).fillna(images.raw_machine)
    images.loc[images.machine.isin(['', 'NA', 'AMBIGUOUS_DEVICE']), 'machine'] = 'Geraet fehlt / mehrdeutig'
    for granularity, freq in [("week","W-SUN"),("month","M"),("quarter","Q"),("year","Y")]:
        result["periods"][granularity] = {}
        for model, all_visits in prepared["visits"].items():
            periods = []
            for period in pd.period_range(profile.start, profile.end, freq=freq):
                a, b = max(profile.start,str(period.start_time.date())), min(profile.end,str(period.end_time.date()))
                selected = images[images.date.between(a,b)]
                visits = all_visits[all_visits.date.between(a,b)].reset_index(drop=True)
                groups = []
                unassigned = []
                for (machine,kind), objects in selected[~selected.therapy_device].groupby(['machine','image_kind']):
                    unassigned.append(dict(machine=machine, kind=kind,
                        objects=len(objects) if objects.patient_key.nunique() >= profile.minimum_patients else None,
                        reason='Nicht einem konfigurierten Behandlungsgeraet zugeordnet'))
                for (machine,kind,equipment_text), objects in selected[selected.therapy_device].groupby(["machine","image_kind","equipment"]):
                    device_visits = visits[visits.machine.eq(machine)]
                    raw_machine = next((raw for raw,label in profile.machines.items() if label == machine), "")
                    device_visits = device_visits.loc[[equipment_label(equipment_for(profile, raw_machine, day)) == equipment_text
                                                      for day in device_visits.date]]
                    lookup = {key:g for key,g in device_visits.groupby(["patient_key","date"])}
                    durations, durations_patients, linked_objects, linked_visits = [], set(), 0, 0
                    for key, items in objects.groupby(["patient_key","date"]):
                        match = lookup.get(key)
                        if match is not None and len(match) == 1:
                            linked_objects += len(items)
                            linked_visits += 1
                            durations.append(float(match.duration.iloc[0]))
                            durations_patients.add(key[0])
                    safe = objects.patient_key.nunique() >= profile.minimum_patients
                    safe_visits = device_visits.patient_key.nunique() >= profile.minimum_patients
                    safe_links = len(durations_patients) >= profile.minimum_patients
                    valid_seconds = objects[objects.seconds.notna()]
                    groups.append(dict(machine=machine, kind=kind, equipment=equipment_text,
                        objects=len(objects) if safe else None,
                        denominator_visits=len(device_visits) if safe_visits else None,
                        matched_objects=linked_objects if safe_links else None,
                        matched_visits=linked_visits if safe_links else None,
                        objects_per_100_visits=100*linked_objects/len(device_visits) if safe_links and safe_visits and len(device_visits) else None,
                        visits_with_objects_pct=100*linked_visits/len(device_visits) if safe_links and safe_visits and len(device_visits) else None,
                        exposure_seconds=distribution(valid_seconds.seconds, set(valid_seconds.patient_key), profile.minimum_patients),
                        visit_duration_minutes=distribution(durations, durations_patients, profile.minimum_patients)))
                groups.sort(key=lambda g:(natural_key(g["machine"]),g["kind"],g["equipment"]))
                periods.append(dict(label=str(period),start=a,end=b,groups=groups,unassigned=unassigned))
            result["periods"][granularity][model] = periods
    return result
