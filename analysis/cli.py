"""python -m analysis.cli export.xlsx --profile profile.json --output report"""
import argparse
import csv
import json
import sys
from pathlib import Path
import pandas as pd
from . import VERSION, cache
from .contracts import load_profile
from .ingest import load_export, normalize_flow
from .throughput import prepare_visits, aggregate
from .flow import summarize
from .metrics import deduplicate
from .report import render


def boolean(value):
    return str(value).casefold() in {"true","1","1.0"}


def suppress_flow(flow,minimum):
    data={k:v for k,v in flow.items() if k not in {"duplicates","series"}}
    hidden={k for k,v in data.items() if isinstance(v,int) and not isinstance(v,bool) and 0<v<minimum}
    partitions=[
        {"completed_counselling_appointments","open_counselling_appointments",
         "cancelled_counselling_appointments","other_counselling_appointments",
         "registered_counselling_appointments","cancellation_pct"},
        {"mature_episodes","matched_mature","observation_mature","unresolved_mature","unresolved_pct",
         "counselling_episodes","provisional"},
    ]
    # Counts of repeated visits plus their episode total can expose a tiny remainder.
    if "multiple_counselling" in hidden:
        hidden.update({"counselling_episodes","completed_counselling_appointments"})
    changed=True
    while changed:
        before=len(hidden)
        for partition in partitions:
            if hidden & partition:
                hidden.update(partition)
        changed=len(hidden)!=before
    for key in hidden:
        if key in data:
            data[key]=None
    return data


def analyze(path,profile):
    metadata,events,coverage,activities = load_export(path)
    for field,value in (("period_start",profile.start),("period_end",profile.end)):
        if str(pd.Timestamp(metadata[field]).date()) != value:
            raise ValueError("Profile period must match export metadata")
    if any(c["is_required"] and not c["available"] for c in coverage):
        raise ValueError("Required source coverage is missing")
    notes = []
    unknown = events[events.source.eq("appointment") &
                     ~events.activity_code.isin(profile.activity_codes)]
    if not unknown.empty:
        notes.append("Nicht zugeordnete Aktivitaeten: Standortprofil vor fachlicher Auswertung vervollstaendigen.")
    if not profile.confirmed:
        notes.append("Standortprofil noch nicht fachlich bestaetigt.")
    confirmed = (profile.confirmed and profile.sources_complete and
                 boolean(metadata.get("data_through_confirmed",False)))
    if not confirmed:
        notes.append("Quellenumfang/Datenstand unbestaetigt: keine belastbare Quote ohne Behandlungsbeginn.")
    flow_events = normalize_flow(events,profile)
    flow = summarize(flow_events,profile,data_through=metadata["data_through"],
                     context_start=metadata["context_start"],sources_complete=confirmed)
    raw_flow=flow
    flow=suppress_flow(flow,profile.minimum_patients)
    if any(v is None and raw_flow.get(k) is not None for k,v in flow.items()):
        notes.append("Kleine Teilgruppen und abhaengige Summen im Patientenfluss unterdrueckt.")
    measurements = events.copy()
    record_fallback_count=0
    if "time_source" in measurements:
        bad_time = measurements.source.isin(["delivery","imaging"]) & measurements.time_source.eq("record_fallback")
        record_fallback_count=int(bad_time.sum())
        measurements.loc[bad_time,["event_start","event_end"]] = None
    prepared = prepare_visits(measurements,profile)
    periods = aggregate(prepared,profile)
    quality = {}
    for key,value in prepared["audit"].items():
        quality[key] = "<5" if 0<value<profile.minimum_patients else value
    quality["unknown_activity_rows"] = "<5" if 0<len(unknown)<profile.minimum_patients else len(unknown)
    quality["source_coverage_confirmed"] = confirmed
    quality["imaging_source"] = "DWH-FactTreatmentHistory; direkte Bildobjekte nicht enthalten"
    quality["profile_confirmed"] = profile.confirmed
    quality["record_timestamp_fallback_rows"]=record_fallback_count
    quality["future_observation_horizon_months"] = 12
    if "source_rows" in events:
        quality["raw_source_rows"] = int(pd.to_numeric(events.source_rows,errors="coerce").sum())
    else:
        quality["raw_source_rows"] = len(events)
    quality["requested_days"] = (pd.Timestamp(profile.end)-pd.Timestamp(profile.start)).days+1
    if quality["requested_days"] not in {365,366}:
        notes.append("Teilzeitraum: kein vollstaendiger Jahresvergleich.")
    return dict(version=VERSION,site=profile.site,start=profile.start,end=profile.end,
                period_reason=profile.period_reason,data_through=str(pd.Timestamp(metadata["data_through"]).date()),
                periods=periods,flow=flow,quality=quality,notes=notes,default_model=profile.model,
                coverage=coverage)


def export_outputs(data,output):
    output.mkdir(parents=True,exist_ok=True)
    render(data,output/"Standortanalyse.html")
    (output/"aggregate.json").write_text(json.dumps(data,indent=2,allow_nan=False),encoding="utf-8")
    records = []
    for granularity,models in data["periods"].items():
        for model,periods in models.items():
            for period in periods:
                for group in period["groups"]:
                    records.append(dict(granularity=granularity,model=model,period=period["label"],
                                        machine=group["machine"],**group["kpi"]))
    if records:
        with (output/"Kennzahlen.csv").open("w",newline="",encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream,fieldnames=list(records[0]),delimiter=";")
            writer.writeheader()
            for row in records:
                # Avoid spreadsheet formula injection in user-configured labels.
                writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(("=","+","-","@")) else v)
                                 for k,v in row.items()})


def main(argv=None):
    parser=argparse.ArgumentParser(description="Lokale Standortanalyse; nur Aggregate werden ausgegeben.")
    parser.add_argument("export",type=Path)
    parser.add_argument("--profile",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--no-cache",action="store_true")
    args=parser.parse_args(argv)
    profile=load_profile(args.profile)
    key=cache.cache_key(args.export,profile)
    database=args.output/"aggregate-cache.sqlite"
    data=None if args.no_cache else cache.get(database,key)
    hit=data is not None
    if data is None:
        data=analyze(args.export,profile)
        cache.put(database,key,data)
    export_outputs(data,args.output)
    print("ANALYSIS_OK cache="+("hit" if hit else "miss")+" method="+VERSION)
    return 0


if __name__=="__main__":
    try:
        sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:
        # No cell values, workbook paths, identities or source credentials in logs.
        print("ANALYSIS_REFUSED: "+type(exc).__name__+
              ". Exportvertrag, Quellen und Profil lokal pruefen.",file=sys.stderr)
        sys.exit(2)
