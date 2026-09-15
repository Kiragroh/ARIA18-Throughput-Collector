"""Inspect a local collector export without printing patient-level records."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.ingest import load_export


def inspect(source, output):
    metadata, events, coverage, activities = load_export(source)
    output.mkdir(parents=True, exist_ok=True)
    times = pd.to_datetime(events.event_start, errors="coerce", format="mixed")
    end = pd.Timestamp(metadata["period_end"]) + pd.Timedelta(days=1)
    selected = events[times.ge(pd.Timestamp(metadata["period_start"])) & times.lt(end)].copy()
    selected["month"] = times.loc[selected.index].dt.strftime("%Y-%m")
    for frame, name, keys in [
        (selected, "activity-status-inventory.csv", ["source", "activity_code", "status", "machine"]),
        (selected, "device-month-inventory.csv", ["source", "machine", "month"]),
    ]:
        frame.groupby(keys, dropna=False).agg(
            rows=("source", "size"), patients=("patient_key", "nunique"),
            first=("event_start", "min"), last=("event_start", "max")
        ).reset_index().to_csv(output / name, index=False, encoding="utf-8-sig")
    pd.DataFrame(activities).to_csv(output / "activity-catalog.csv", index=False, encoding="utf-8-sig")
    data = dict(metadata=metadata, coverage=coverage, rows=len(events),
                period_rows=len(selected), sources=selected.source.value_counts().to_dict(),
                exact_duplicate_rows=int(events.duplicated().sum()),
                duplicate_event_keys=int(events.duplicated(["source", "event_key"]).sum()),
                missing_start=int(times.isna().sum()),
                source_sha256=hashlib.file_digest(source.open("rb"), "sha256").hexdigest())
    (output / "audit.json").write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
    # This cache still contains pseudonymized events and must stay on protected storage.
    for key in ("period_start", "period_end", "context_start", "data_through", "data_through_confirmed"):
        events[key] = metadata[key]
    events.to_csv(output / "events-local.csv", index=False, encoding="utf-8-sig")
    print("LOCAL_INSPECTION_OK rows=" + str(len(events)) + " period_rows=" + str(len(selected)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inspect(args.export, args.output)
