"""Read an SSRS workbook once, never execute formulas or external workbook links."""
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook


def load_export(path: Path):
    if path.suffix.casefold()==".csv":
        events=pd.read_csv(path,dtype=str,keep_default_na=False,encoding="utf-8-sig").replace("",None)
        meta_fields={"contract_version","run_id","period_start","period_end","context_start",
                     "data_through","data_through_confirmed"}
        if events.empty or not meta_fields <= set(events):
            raise ValueError("Incomplete flat export metadata")
        meta_fields |= {"site", "period_reason"} & set(events)
        meta_rows=events[sorted(meta_fields)].drop_duplicates()
        if len(meta_rows)!=1 or str(meta_rows.iloc[0].contract_version)!="2.0":
            raise ValueError("Mixed or unsupported flat export contract")
        required={"source","event_key","patient_key","event_start","event_end","status","machine","activity_code"}
        if not required <= set(events):
            raise ValueError("Incomplete flat event contract")
        return meta_rows.iloc[0].to_dict(),events,[],[]
    tables = {"00_Metadata":[],"01_Capabilities":[],"02_Activities":[],"90_Events":[]}
    with path.open("rb") as stream:
        workbook = load_workbook(stream,read_only=True,data_only=True,keep_links=False)
        try:
            for sheet in workbook:
                prefix = next((key for key in tables if sheet.title.startswith(key)),None)
                if not prefix:
                    continue
                headers = None
                for i,values in enumerate(sheet.iter_rows(values_only=True)):
                    if headers is None:
                        if "contract_version" in values or "activity_code" in values:
                            headers = [(j,str(v)) for j,v in enumerate(values) if v is not None]
                        elif i>40:
                            break
                        continue
                    record = {name:values[j] if j<len(values) else None for j,name in headers}
                    if not any(v is not None for v in record.values()):
                        continue
                    if record.get(headers[0][1]) == headers[0][1]:
                        continue
                    tables[prefix].append(record)
        finally:
            workbook.close()
    metadata = tables["00_Metadata"]
    if len(metadata)!=1 or str(metadata[0].get("contract_version")) not in {"2.0","2"}:
        raise ValueError("Unsupported export contract; collect with RDL 2.0")
    events = pd.DataFrame(tables["90_Events"])
    if events.empty:
        raise ValueError("No event details: check collection_state, capabilities and export version")
    required = {"source","event_key","patient_key","event_start","event_end","status","machine","activity_code"}
    if not required <= set(events):
        raise ValueError("Incomplete event contract")
    if events.get("run_id",pd.Series(dtype=str)).nunique()!=1:
        raise ValueError("Mixed or missing run identity")
    if events.run_id.iloc[0] != metadata[0].get("run_id"):
        raise ValueError("Run identity differs from metadata")
    return metadata[0],events,tables["01_Capabilities"],tables["02_Activities"]


def normalize_flow(events, profile):
    frame = events.copy()
    frame["kind"] = frame.activity_code.map(profile.activity_codes).fillna("unknown")
    delivered = frame.source.eq("delivery")
    brachy = pd.to_numeric(frame.get("is_brachy",pd.Series(0,index=frame.index)),errors="coerce").eq(1)
    frame.loc[delivered & ~brachy,"kind"] = "treatment_external"
    frame.loc[delivered & brachy,"kind"] = "treatment_brachy"
    # Imaging is never a treatment-start event by itself.
    frame = frame[~frame.source.eq("imaging") & frame.patient_key.notna()]
    return frame
