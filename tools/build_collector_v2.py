"""Build the v2 collector. Source adapters emit only allowlisted columns."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import math
try:
    from . import build_rdl as layout
except ImportError:
    import build_rdl as layout

ROOT = Path(__file__).resolve().parents[1]
NS = {"r":"http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}
PARAMETERS = {
    "PeriodStart":("DateTime",'=DateSerial(2025, 1, 1)',"Auswertung von"),
    "PeriodEnd":("DateTime",'=DateSerial(2025, 12, 31)',"Auswertung bis"),
    "PeriodReason":("String",'=IIf(Parameters!PeriodStart.Value = DateSerial(2025,1,1) And Parameters!PeriodEnd.Value = DateSerial(2025,12,31), "Standardjahr 2025", "Abweichender Zeitraum")',None),
    "ContextStart":("DateTime",'=DateAdd("yyyy", -1, Parameters!PeriodStart.Value)',None),
    "DataThrough":("DateTime",'=Today().AddDays(-1)',None),
    "DataThroughConfirmed":("Boolean","false",None),
    "SiteLabel":("String","\u00c4ndere mich","Standort / Klinik"),
    "IncludePseudonymizedDetails":("Boolean","true",None),
    "RunId":("String",'=System.Guid.NewGuid().ToString("N")',None),
    "ExportSalt":("String",'=System.Guid.NewGuid().ToString("N")',None),
}
# Column names are code constants, never interpolated from a site's profile.
SOURCES = {
    "Patient":("DWH.DimPatient",[
        ("DimPatientID","bigint",True),("IsMOTestPatient","int",True),
        ("PatientId","nvarchar(255)",False),("PatientLastName","nvarchar(255)",False)]),
    "Machine":("DWH.DimMachine",[
        ("DimMachineID","bigint",True),("MachineId","nvarchar(255)",True)]),
    "Treatment":("DWH.FactTreatmentHistory",[
        ("DimPatientID","bigint",True),("DimCourseID","bigint",False),
        ("DimPlanID","bigint",False),("DimFieldID","bigint",False),
        ("DimActualMachineID","bigint",False),("DimPlanMachineID","bigint",False),
        ("TreatmentRecordDateTime","datetime2",True),
        ("TreatmentStartTime","datetime2",False),("TreatmentEndTime","datetime2",False),
        ("FractionNumber","int",False),("IsImage","int",True),("IsBrachy","int",True),
        ("FractionsPlanned","int",False),
        ("DeliveredMU","float",False),("FieldMUActual","float",False),("DoseDelivered","float",False)]),
    "Plan":("DWH.DimPlan",[
        ("DimPlanID","bigint",False),("NoFractionsPlanned","int",False),
        ("FirstDayOfTreatment","datetime2",False),("LastDayOfTreatment","datetime2",False)]),
    "Appointment":("DWH.DimActivityTransaction",[
        ("DimActivityTransactionID","bigint",True),("DimPatientID","bigint",True),
        ("DimActivityID","bigint",True),("AppointmentDateTime","datetime2",True),
        ("ScheduledEndTime","datetime2",False),("ActivityStartDateTime","datetime2",False),
        ("ActivityEndDateTime","datetime2",False),("AppointmentStatus","nvarchar(255)",True),
        ("DerivedAppointmentTaskDate","datetime2",False),
        ("AppointmentResourceStatus","nvarchar(255)",False),("IsScheduled","nvarchar(50)",False),
        ("ctrResourceSer","bigint",False),("DimResourceID","bigint",False)]),
    "Activity":("DWH.DimActivity",[
        ("DimActivityID","bigint",True),("ActivityCode","nvarchar(255)",True),
        ("ActivityNameDEU","nvarchar(1000)",False),("ActivityCategoryDEU","nvarchar(1000)",False)]),
    "Resource":("DWH.vv_ResourceInfo",[
        ("ctrResourceSer","bigint",False),("ResourceId","nvarchar(255)",False)]),
    "ResourceMachine":("DWH.InSightiveResourceMachine",[
        ("DimResourceID","bigint",False),("MachineId","nvarchar(255)",False)]),
    "History":("DWH.DimActivityTransactionHistory",[
        ("DimActivityTransactionID","bigint",False),
        ("ScheduledActivityHstryDateTime","datetime2",False),
        ("ScheduledActivityCode","nvarchar(255)",False)]),
}
FIELDS = ["contract_version","run_id","source","event_key","patient_key","course_key","plan_key",
          "machine","event_start","event_end","fraction","activity_code","status","is_brachy",
          "activity_start","activity_end","completed","time_source","completion_candidates","source_rows",
          "activity_name","activity_category","milestone_time","resource_status","patient_class",
          "planned_fractions","plan_first_treatment","plan_last_treatment"]


def lit(value):
    return "N'"+value.replace("'","''")+"'"


def stage(name, inventory=False):
    table,columns = SOURCES[name]
    required = [col for col,_,mandatory in columns if mandatory]
    checks = "\n".join(f"IF COL_LENGTH(N'{table}',N'{col}') IS NULL THROW 51001, N'Required source unavailable: {table}.{col}', 1;"
                       for col in required)
    expressions = []
    for col,type_,mandatory in columns:
        present = lit(f"TRY_CONVERT({type_}, s.[{col}])")
        missing = lit(f"CAST(NULL AS {type_})")
        expressions.append(present if mandatory else
                           f"CASE WHEN COL_LENGTH(N'{table}',N'{col}') IS NOT NULL THEN {present} ELSE {missing} END")
    sql = f"CREATE TABLE #{name} ("+", ".join(f"[{col}] {type_} NULL" for col,type_,_ in columns)+");\n"+checks+"\n"
    where = ""
    if name=="Treatment":
        where = " WHERE s.TreatmentRecordDateTime >= @context AND s.TreatmentRecordDateTime < DATEADD(day,1,@through) AND EXISTS(SELECT 1 FROM #Cohort c WHERE c.patient_id=s.DimPatientID)"
    if name=="Plan":
        where = " WHERE EXISTS(SELECT 1 FROM #Treatment t WHERE t.DimPlanID=s.DimPlanID)"
    if name=="Appointment":
        where = " WHERE s.AppointmentDateTime >= @context AND s.AppointmentDateTime < DATEADD(month,12,DATEADD(day,1,@through)) AND (COALESCE(s.DimPatientID,0)<=0 OR EXISTS(SELECT 1 FROM #Cohort c WHERE c.patient_id=s.DimPatientID))"
    if name=="History":
        where = (" WHERE EXISTS(SELECT 1 FROM #Appointment a WHERE a.DimActivityTransactionID=s.DimActivityTransactionID)"
                 " AND s.ScheduledActivityHstryDateTime >= @context AND s.ScheduledActivityHstryDateTime < DATEADD(day,2,@through)")
    if inventory and name=='Appointment':
        where=' WHERE s.AppointmentDateTime>=@context AND s.AppointmentDateTime<DATEADD(day,1,@through)'
    if inventory and name=='Treatment':
        where=' WHERE s.TreatmentRecordDateTime>=@context AND s.TreatmentRecordDateTime<DATEADD(day,1,@through)'
    condition = " AND ".join(f"COL_LENGTH(N'{table}',N'{col}') IS NOT NULL" for col in
                            (["DimActivityTransactionID","ScheduledActivityHstryDateTime","ScheduledActivityCode"] if name=="History"
                             else ["DimPlanID"] if name=="Plan" else []))
    sql += f"IF OBJECT_ID(N'{table}') IS NOT NULL"+(" AND "+condition if condition else "")+"\nBEGIN\n"
    select_expression = " + N', ' + ".join(expressions)
    sql += f"DECLARE @sql_{name} nvarchar(max) = N'INSERT INTO #{name} SELECT ' + {select_expression} + {lit(' FROM '+table+' s'+where)};\n"
    first,last=('PeriodStart','PeriodEnd') if inventory else ('ContextStart','DataThrough')
    sql += f"EXEC sys.sp_executesql @sql_{name}, N'@context date,@through date', @context= @{first}, @through= @{last};\nEND;\n"
    return sql


def capabilities():
    values = ",\n".join(f"({lit(table)},{lit(col)},{1 if required else 0})"
                          for table,columns in SOURCES.values() for col,_,required in columns)
    return ("SELECT N'2.0' AS contract_version, source_name, column_name, is_required,"
            " CASE WHEN COL_LENGTH(source_name,column_name) IS NULL THEN 0 ELSE 1 END AS available"
            " FROM (VALUES "+values+") v(source_name,column_name,is_required)"
            " UNION ALL SELECT N'2.0',N'DWH.FactTreatmentHistory',N'delivery_evidence_any_of_MU_or_dose',1,"
            "CASE WHEN "+delivery_evidence_missing()+" THEN 0 ELSE 1 END;")


def delivery_evidence_missing():
    return " AND ".join("COL_LENGTH(N'DWH.FactTreatmentHistory',N'"+column+"') IS NULL"
                        for column in ("DeliveredMU","FieldMUActual","DoseDelivered"))


def source_gaps():
    required = [f"COL_LENGTH(N'{table}',N'{column}') IS NULL"
                for table, columns in SOURCES.values() for column, _, needed in columns if needed]
    return " OR ".join(required+["("+delivery_evidence_missing()+")"])


def event_sql():
    guard = """
SET NOCOUNT ON;
SET @PeriodStart=CAST(@PeriodStart AS date);
SET @PeriodEnd=CAST(@PeriodEnd AS date);
SET @ContextStart=CAST(@ContextStart AS date);
SET @DataThrough=CAST(@DataThrough AS date);
IF CAST(@PeriodStart AS date) > CAST(@PeriodEnd AS date) OR @ContextStart > @PeriodStart
  OR @DataThrough < @PeriodEnd OR @DataThrough >= CAST(GETDATE() AS date)
  THROW 51000, N'Invalid period/context/data watermark. Use complete past dates.', 1;
IF DATEDIFF(day,@ContextStart,@DataThrough)>1827
  THROW 51000, N'Context larger than five years: split extraction.', 1;
IF @IncludePseudonymizedDetails=0 OR """+source_gaps()+"""
BEGIN
 SELECT """+",".join(f"CAST(NULL AS {'datetime2' if f in ['event_start','event_end','activity_start','activity_end','completed'] else 'nvarchar(255)'}) AS [{f}]" for f in FIELDS)+""" WHERE 1=0;
 RETURN;
END;
"""
    cohort_checks="\n".join(
        f"IF COL_LENGTH(N'{table}',N'{column}') IS NULL THROW 51001,N'Missing cohort source',1;"
        for table,column in [("DWH.DimActivityTransaction","DimPatientID"),
                              ("DWH.DimActivityTransaction","AppointmentDateTime"),
                              ("DWH.FactTreatmentHistory","DimPatientID"),
                              ("DWH.FactTreatmentHistory","TreatmentRecordDateTime")])
    cohort_sql="""
CREATE TABLE #Cohort(patient_id bigint NOT NULL PRIMARY KEY);
DECLARE @cohort_sql nvarchar(max)=N'
 INSERT INTO #Cohort
 SELECT DimPatientID FROM DWH.DimActivityTransaction
 WHERE AppointmentDateTime>=@context AND AppointmentDateTime<DATEADD(day,1,@end) AND DimPatientID>0
 UNION
 SELECT DimPatientID FROM DWH.FactTreatmentHistory
 WHERE TreatmentRecordDateTime>=@context AND TreatmentRecordDateTime<DATEADD(day,1,@end) AND DimPatientID>0';
EXEC sys.sp_executesql @cohort_sql,N'@context date,@end date',@context=@ContextStart,@end=@PeriodEnd;
"""
    sources = "".join(stage(name)+("CREATE INDEX ix_appointment_id ON #Appointment(DimActivityTransactionID);\n" if name=="Appointment" else "") for name in SOURCES)
    checks = """
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'DeliveredMU') IS NULL
 AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'FieldMUActual') IS NULL
 AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'DoseDelivered') IS NULL
 THROW 51001, N'No delivery evidence column available', 1;
CREATE INDEX ix_history_id ON #History(DimActivityTransactionID,ScheduledActivityHstryDateTime);
CREATE INDEX ix_patient_id ON #Patient(DimPatientID);
;WITH plan_info AS (
 SELECT DimPlanID,
 CASE WHEN COUNT(DISTINCT NoFractionsPlanned)=1 THEN MAX(NoFractionsPlanned) END AS planned_fractions,
 MIN(FirstDayOfTreatment) AS first_treatment,MAX(LastDayOfTreatment) AS last_treatment
 FROM #Plan GROUP BY DimPlanID
), resource_map AS (
 SELECT DISTINCT a.DimActivityTransactionID, m.MachineId
 FROM #Appointment a
 JOIN #Resource r ON r.ctrResourceSer=a.ctrResourceSer
 JOIN #Machine m ON m.MachineId=r.ResourceId
 UNION
 SELECT DISTINCT a.DimActivityTransactionID, m.MachineId
 FROM #Appointment a
 JOIN #ResourceMachine r ON r.DimResourceID=a.DimResourceID
 JOIN #Machine m ON m.MachineId=r.MachineId
), appointment_devices AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,
 CASE WHEN COUNT(DISTINCT r.MachineId)=1 THEN MIN(r.MachineId)
      WHEN COUNT(DISTINCT r.MachineId)>1 THEN N'AMBIGUOUS_DEVICE' ELSE N'' END AS machine
 FROM #Appointment a LEFT JOIN resource_map r ON r.DimActivityTransactionID=a.DimActivityTransactionID
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime
), events AS (
 SELECT
 CASE WHEN t.IsImage=1 THEN N'imaging' ELSE N'delivery' END AS source,
 CONCAT(N'T:',t.DimPatientID,N':',t.DimCourseID,N':',t.DimPlanID,N':',t.DimFieldID,N':',
        COALESCE(t.DimActualMachineID,t.DimPlanMachineID),N':',t.FractionNumber,N':',t.IsImage,N':',
        CONVERT(nvarchar(33),t.TreatmentRecordDateTime,126),N':',
        CONVERT(nvarchar(33),t.TreatmentStartTime,126)) AS identity_key,
 t.DimPatientID,t.DimCourseID,t.DimPlanID,COALESCE(am.MachineId,pm.MachineId,N'') AS machine,
 COALESCE(t.TreatmentStartTime,t.TreatmentRecordDateTime) AS event_start,
 t.TreatmentEndTime AS event_end,t.FractionNumber AS fraction,
 CAST(N'' AS nvarchar(255)) AS activity_code,CAST(N'delivered' AS nvarchar(255)) AS status,
 t.IsBrachy AS is_brachy,CAST(NULL AS datetime2) AS activity_start,
 CAST(NULL AS datetime2) AS activity_end,CAST(NULL AS datetime2) AS completed,
 CASE WHEN t.TreatmentStartTime IS NOT NULL THEN N'measured' ELSE N'record_fallback' END AS time_source,
 CAST(NULL AS int) AS completion_candidates,
 CAST(N'' AS nvarchar(1000)) AS activity_name,CAST(N'' AS nvarchar(1000)) AS activity_category,
 t.TreatmentRecordDateTime AS milestone_time,CAST(N'' AS nvarchar(255)) AS resource_status,
 CASE WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END AS patient_class,
 COALESCE(pl.planned_fractions,t.FractionsPlanned) AS planned_fractions,
 pl.first_treatment AS plan_first_treatment,pl.last_treatment AS plan_last_treatment
 FROM #Treatment t JOIN #Patient p ON p.DimPatientID=t.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #Machine am ON am.DimMachineID=t.DimActualMachineID
 LEFT JOIN #Machine pm ON pm.DimMachineID=t.DimPlanMachineID
 LEFT JOIN plan_info pl ON pl.DimPlanID=t.DimPlanID
 WHERE t.DimPatientID>0 AND (t.IsImage=1 OR COALESCE(t.DeliveredMU,0)>0
                           OR COALESCE(t.FieldMUActual,0)>0 OR COALESCE(t.DoseDelivered,0)>0)
 UNION ALL
 SELECT N'appointment',
 CONCAT(N'A:',a.DimPatientID,N':',a.DimActivityID,N':',CONVERT(nvarchar(33),a.AppointmentDateTime,126)),
 a.DimPatientID,CAST(NULL AS bigint),CAST(NULL AS bigint),COALESCE(r.machine,N''),
 a.AppointmentDateTime,a.ScheduledEndTime,CAST(NULL AS int),act.ActivityCode,
 a.AppointmentStatus,0,
 a.ActivityStartDateTime,a.ActivityEndDateTime,
 h.completed,N'calendar',h.candidate_count,
 act.ActivityNameDEU,act.ActivityCategoryDEU,
 COALESCE(a.DerivedAppointmentTaskDate,a.AppointmentDateTime),a.AppointmentResourceStatus,
 CASE WHEN COALESCE(a.DimPatientID,0)<=0 THEN N'no_patient'
      WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END,
 CAST(NULL AS int),CAST(NULL AS datetime2),CAST(NULL AS datetime2)
 FROM #Appointment a JOIN #Activity act ON act.DimActivityID=a.DimActivityID
 LEFT JOIN #Patient p ON p.DimPatientID=a.DimPatientID
 LEFT JOIN appointment_devices r ON (r.DimPatientID=a.DimPatientID OR (r.DimPatientID IS NULL AND a.DimPatientID IS NULL))
  AND r.DimActivityID=a.DimActivityID AND r.AppointmentDateTime=a.AppointmentDateTime
 OUTER APPLY (
  SELECT MIN(h.ScheduledActivityHstryDateTime) AS completed,COUNT(DISTINCT h.ScheduledActivityHstryDateTime) AS candidate_count
  FROM #History h WHERE h.DimActivityTransactionID=a.DimActivityTransactionID
   AND UPPER(h.ScheduledActivityCode) IN (N'COMPLETED',N'MANUALLY COMPLETED',N'COMPLTFINISH',N'PT. COMPLTFINISH')
   AND h.ScheduledActivityHstryDateTime >= COALESCE(a.ActivityStartDateTime,a.AppointmentDateTime)
   AND h.ScheduledActivityHstryDateTime < DATEADD(hour,12,a.AppointmentDateTime)
 ) h
 WHERE ((a.DimPatientID>0 AND p.IsMOTestPatient=0) OR (COALESCE(a.DimPatientID,0)<=0
   AND a.AppointmentDateTime>=@PeriodStart AND a.AppointmentDateTime<DATEADD(day,1,@PeriodEnd)))
  AND COALESCE(a.IsScheduled,N'Y')=N'Y'
  AND COALESCE(a.AppointmentResourceStatus,N'')<>N'Deleted'
  AND COALESCE(a.AppointmentStatus,N'')<>N'Deleted'
), keyed_events AS (
 SELECT *, CASE WHEN source=N'appointment' THEN identity_key ELSE
  CONCAT(source,N':',DimPatientID,N':',DimCourseID,N':',DimPlanID,N':',machine,N':',
         CONVERT(nvarchar(10),event_start,23),N':',fraction,N':',time_source) END AS compact_key
 FROM events
), grouped_events AS (
 SELECT source,compact_key AS identity_key,DimPatientID,DimCourseID,DimPlanID,machine,
 MIN(event_start) AS event_start,MAX(event_end) AS event_end,fraction,activity_code,status,is_brachy,
 MIN(activity_start) AS activity_start,MAX(activity_end) AS activity_end,
 CASE WHEN COUNT(DISTINCT completed)<=1 THEN MIN(completed) END AS completed,
 time_source,MAX(completion_candidates) AS completion_candidates,COUNT_BIG(*) AS source_rows,
 MAX(activity_name) AS activity_name,MAX(activity_category) AS activity_category,
 MIN(milestone_time) AS milestone_time,MIN(resource_status) AS resource_status,
 MAX(patient_class) AS patient_class,
 CASE WHEN COUNT(DISTINCT planned_fractions)=1 THEN MAX(planned_fractions) END AS planned_fractions,
 MIN(plan_first_treatment) AS plan_first_treatment,MAX(plan_last_treatment) AS plan_last_treatment
 FROM keyed_events
 GROUP BY source,compact_key,DimPatientID,DimCourseID,DimPlanID,machine,fraction,activity_code,status,is_brachy,time_source
)
SELECT N'2.0' AS contract_version,@RunId AS run_id,source,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':E:',identity_key)),2) AS event_key,
 CASE WHEN DimPatientID>0 THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':P:',DimPatientID)),2) END AS patient_key,
 CASE WHEN DimCourseID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':C:',DimCourseID)),2) END AS course_key,
 CASE WHEN DimPlanID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':L:',DimPlanID)),2) END AS plan_key,
 machine,event_start,event_end,fraction,activity_code,status,is_brachy,activity_start,activity_end,
 completed,time_source,completion_candidates,source_rows,
 activity_name,activity_category,milestone_time,resource_status,patient_class,
 planned_fractions,plan_first_treatment,plan_last_treatment
FROM grouped_events
ORDER BY event_start,source;
"""
    return guard+cohort_checks+cohort_sql+sources+checks


def build(include_inventory=True):
    if __package__:
        from . import imaging_objects_v2 as image_adapter
    else:
        import imaging_objects_v2 as image_adapter
    metadata_fields = ["contract_version","run_id","site","period_start","period_end","period_reason",
                       "context_start","data_through","data_through_confirmed","details_included",
                       "collector_release","tested_aria_major","aria_version_status","collection_state",
                       "comparison_population_complete", "image_objects_state"]
    queries = {
        "Metadata": "SELECT N'2.0' AS contract_version,@RunId AS run_id,@SiteLabel AS site,"
        "@PeriodStart AS period_start,@PeriodEnd AS period_end,@PeriodReason AS period_reason,"
        "@ContextStart AS context_start,@DataThrough AS data_through,"
        "@DataThroughConfirmed AS data_through_confirmed,@IncludePseudonymizedDetails AS details_included,"
        "N'2.0.0-rc.4' AS collector_release,N'18' AS tested_aria_major,N'NOT_DETECTED_FROM_DWH' AS aria_version_status,"
        "1 AS comparison_population_complete,"
        "CASE WHEN "+image_adapter.missing()+" THEN N'UNAVAILABLE' ELSE N'AVAILABLE' END AS image_objects_state,"
        "CASE WHEN "+source_gaps()+" THEN N'EVENTS_UNAVAILABLE_CHECK_CAPABILITIES' ELSE N'READY' END AS collection_state;",
        "Capabilities":capabilities(),
        "ActivityCatalog":stage("Activity")+"SELECT DISTINCT ActivityCode AS activity_code,ActivityNameDEU AS activity_name,ActivityCategoryDEU AS activity_category FROM #Activity ORDER BY activity_code;",
        "EventDetails":event_sql()
    }
    fields = dict(Metadata=metadata_fields,
                  Capabilities=["contract_version","source_name","column_name","is_required","available"],
                  ActivityCatalog=["activity_code","activity_name","activity_category"],
                  EventDetails=FIELDS)
    if include_inventory:
        try:
            from .build_preflight_v2 import queries as inventory_queries, guarded
        except ImportError:
            from build_preflight_v2 import queries as inventory_queries, guarded
        queries["ActivityCatalog"] = guarded(["Activity"],fields["ActivityCatalog"],queries["ActivityCatalog"])
        for name, (sql, columns) in inventory_queries().items():
            queries[name], fields[name] = sql, columns
        queries["ImageObjects"], fields["ImageObjects"] = image_adapter.query(), image_adapter.FIELDS
        queries["EventDetails"] = queries.pop("EventDetails")
    sql_dir = ROOT/"sql/v2"
    sql_dir.mkdir(parents=True,exist_ok=True)
    # Reuse the tested RDL table/parameter rendering layer with the v2 contract.
    layout.FIELDS = fields
    layout.PAGE_NAMES = {"Metadata":"00_Metadata","Capabilities":"01_Capabilities",
                         "ActivityCatalog":"02_Activities","EventDetails":"90_Events", "ImageObjects":"91_Images"}
    layout.CAPTIONS = {"Metadata":"Exportvertrag und Auswertungszeitraum","Capabilities":"Quellenabdeckung",
                       "ActivityCatalog":"Lokales Aktivitaetsinventar","EventDetails":"Lokale pseudonymisierte Ereignisse",
                       "ImageObjects":"Bildobjekte: lokale pseudonymisierte Zusatzquelle"}
    for i, name in enumerate(n for n in queries if n not in layout.PAGE_NAMES):
        layout.PAGE_NAMES[name] = str(i+3).zfill(2)+"_"+name
        layout.CAPTIONS[name] = name
    layout.REPORT_PARAMETERS = list(PARAMETERS)
    datasets = []
    for name,sql in queries.items():
        (sql_dir/(name+".sql")).write_text(sql,encoding="utf-8")
        old = layout._compose_sql
        try:
            layout._compose_sql = lambda _: sql
            dataset = layout._dataset_xml(name,"")
        finally:
            layout._compose_sql = old
        datasets.append(dataset.replace("<rd:UseGenericDesigner>","<Timeout>600</Timeout><rd:UseGenericDesigner>"))
    params = []
    cells = []
    from xml.sax.saxutils import escape
    for i,(name,(type_,default,prompt)) in enumerate(PARAMETERS.items()):
        end = f"<Prompt>{escape(prompt)}</Prompt>" if prompt else "<Hidden>true</Hidden>"
        optional = "<AllowBlank>true</AllowBlank>" if type_ == "String" and name in {"SiteLabel", "PeriodReason"} else ""
        params.append(f'<ReportParameter Name="{name}"><DataType>{type_}</DataType>{optional}<DefaultValue><Values><Value>{escape(default)}</Value></Values></DefaultValue>{end}</ReportParameter>')
        cells.append(f"<CellDefinition><ColumnIndex>{i%4}</ColumnIndex><RowIndex>{i//4}</RowIndex><ParameterName>{name}</ParameterName></CellDefinition>")
    items = [layout._textbox("Title","ARIA 18 | Full Collector 2.0 | Auswertung und Quellenpruefung",0,2,396,13,size=18,bold=True),
             layout._textbox("Note","Standardjahr 2025. Vorlauf und Nachbeobachtung automatisch. Pseudonymisierte Auswertungsdaten: lokal oder mit lokaler Freigabe im geschuetzten Projektbereich verarbeiten, niemals auf GitHub. Keine klinische Entscheidungsunterstuetzung.",16,2,396,20)]
    top = 40
    for name in queries:
        table,top = layout._tablix(name,top)
        if name in {"EventDetails", "ImageObjects"}:
            # Millions of long hash cells do not need multiline print measurement.
            # This changes row layout only; the full Excel cell values stay intact.
            element = ET.fromstring(table)
            group = next(g for g in element.iter("Group") if g.get("Name") == name+"_Year")
            group.set("Name", name+"_Month")
            group.find("GroupExpressions/GroupExpression").text = '=Format(Fields!event_start.Value, "yyyy_MM")'
            group.find("PageName").text = '="'+layout.PAGE_NAMES[name]+'_" & Format(Fields!event_start.Value, "yyyy_MM")'
            for box in element.iter("Textbox"):
                if box.get("Name", "").startswith(name+"_D_"):
                    box.find("CanGrow").text = "false"
                    box.find("KeepTogether").text = "false"
            table = ET.tostring(element, encoding="unicode")
        items.append(table)
    template = (ROOT/"templates/ARIA18_Collector.template.rdl").read_text(encoding="utf-8")
    replace = {"DATASETS":"\n".join(datasets),"REPORT_ITEMS":"\n".join(items),"BODY_HEIGHT":str(top),
               "PAGE_HEADER":layout._textbox("Header","ARIA Throughput | 2.0",0,2,396,7,size=8),
               "PAGE_FOOTER":layout._textbox("Footer","Lokaler Forschungsdatensatz | Nicht zur direkten Weitergabe",0,2,396,7,size=8),
               "REPORT_PARAMETERS":"\n".join(params),
               "PARAMETER_LAYOUT":"\n".join(cells)}
    for token,value in replace.items():
        template = template.replace("{{"+token+"}}",value)
    template = template.replace("<Value>ARIA18_Durchsatz_Klinikvergleich_Collector</Value>",
                                "<Value>ARIA18_Throughput_Collector_2.0</Value>")
    template = template.replace("fbc7de2f-80a7-4b66-bbe4-5135857e6ac7","a1a5210f-7e8a-459e-84f7-ec4f27228a30")
    ET.fromstring(template)
    target = ROOT/"dist/ARIA18_Throughput_Collector_2.0.rdl"
    target.write_text(template,encoding="utf-8")
    return target


if __name__=="__main__":
    print(build())
