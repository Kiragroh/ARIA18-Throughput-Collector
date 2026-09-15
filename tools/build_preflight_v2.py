"""Aggregate-only source and convention inventory before a site's first collection."""
import xml.etree.ElementTree as ET
try:
    from . import build_rdl as layout
    from .build_collector_v2 import build,NS,SOURCES,stage
except ImportError:
    import build_rdl as layout
    from build_collector_v2 import build,NS,SOURCES,stage


def guarded(names,fields,query):
    missing=[]
    for name in names:
        table,columns=SOURCES[name]
        missing.extend(f"COL_LENGTH(N'{table}',N'{c}') IS NULL" for c,_,required in columns if required)
    empty=', '.join(("N'SOURCE_UNAVAILABLE'" if f=='source_state' else 'CAST(NULL AS nvarchar(255))')+' AS ['+f+']' for f in fields)
    return 'SET NOCOUNT ON;\nIF '+ ' OR '.join(missing)+'\nBEGIN SELECT '+empty+'; RETURN; END;\n'+query


def queries():
    af=['source_state','activity_code','activity_name','appointment_status','machine',
        'distinct_appointments','resource_rows','with_activity_start','with_activity_end',
        'with_calendar_end','plausible_activity_intervals']
    appointment=''.join(stage(n,True) for n in ['Patient','Activity','Machine','Resource','ResourceMachine','Appointment'])+"""
;WITH resources AS (
 SELECT DISTINCT a.DimActivityTransactionID,m.MachineId FROM #Appointment a
 JOIN #Resource r ON r.ctrResourceSer=a.ctrResourceSer JOIN #Machine m ON m.MachineId=r.ResourceId
 UNION
 SELECT DISTINCT a.DimActivityTransactionID,m.MachineId FROM #Appointment a
 JOIN #ResourceMachine r ON r.DimResourceID=a.DimResourceID JOIN #Machine m ON m.MachineId=r.MachineId
), devices AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,
 CASE WHEN COUNT(DISTINCT r.MachineId)=1 THEN MIN(r.MachineId)
      WHEN COUNT(DISTINCT r.MachineId)>1 THEN N'AMBIGUOUS_DEVICE' ELSE N'UNMAPPED' END AS machine
 FROM #Appointment a LEFT JOIN resources r ON r.DimActivityTransactionID=a.DimActivityTransactionID
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime
), appointments AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,d.machine,
 COUNT_BIG(*) AS resource_rows,MAX(a.ActivityStartDateTime) AS activity_start,
 MAX(a.ActivityEndDateTime) AS activity_end,MAX(a.ScheduledEndTime) AS calendar_end
 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 JOIN devices d ON d.DimPatientID=a.DimPatientID AND d.DimActivityID=a.DimActivityID AND d.AppointmentDateTime=a.AppointmentDateTime
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,d.machine
)
SELECT N'AVAILABLE' AS source_state,act.ActivityCode AS activity_code,MAX(act.ActivityNameDEU) AS activity_name,
 a.AppointmentStatus AS appointment_status,a.machine,COUNT_BIG(*) AS distinct_appointments,
 SUM(a.resource_rows) AS resource_rows,SUM(CASE WHEN activity_start IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_start,
 SUM(CASE WHEN activity_end IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_end,
 SUM(CASE WHEN calendar_end IS NOT NULL THEN 1 ELSE 0 END) AS with_calendar_end,
 SUM(CASE WHEN DATEDIFF(second,activity_start,activity_end)>0 AND DATEDIFF(second,activity_start,activity_end)<=14400 THEN 1 ELSE 0 END) AS plausible_activity_intervals
FROM appointments a JOIN #Activity act ON act.DimActivityID=a.DimActivityID
GROUP BY act.ActivityCode,a.AppointmentStatus,a.machine ORDER BY act.ActivityCode,a.machine,a.AppointmentStatus;
"""
    mf=['source_state','machine','record_type','source_rows','with_technical_start','with_technical_end','with_delivery_evidence']
    machine=''.join(stage(n,True) for n in ['Patient','Machine','Treatment'])+"""
;WITH tx AS (
 SELECT t.*,COALESCE(am.MachineId,pm.MachineId,N'UNMAPPED') AS machine
 FROM #Treatment t JOIN #Patient p ON p.DimPatientID=t.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #Machine am ON am.DimMachineID=t.DimActualMachineID
 LEFT JOIN #Machine pm ON pm.DimMachineID=t.DimPlanMachineID
)
SELECT N'AVAILABLE' AS source_state,machine,
 CASE WHEN IsImage=1 THEN N'imaging' WHEN IsBrachy=1 THEN N'brachy' ELSE N'treatment_candidate' END AS record_type,
 COUNT_BIG(*) AS source_rows,
 SUM(CASE WHEN TreatmentStartTime IS NOT NULL THEN 1 ELSE 0 END) AS with_technical_start,
 SUM(CASE WHEN TreatmentEndTime IS NOT NULL THEN 1 ELSE 0 END) AS with_technical_end,
 SUM(CASE WHEN COALESCE(DeliveredMU,0)>0 OR COALESCE(FieldMUActual,0)>0 OR COALESCE(DoseDelivered,0)>0 THEN 1 ELSE 0 END) AS with_delivery_evidence
FROM tx GROUP BY machine,CASE WHEN IsImage=1 THEN N'imaging' WHEN IsBrachy=1 THEN N'brachy' ELSE N'treatment_candidate' END
UNION ALL
SELECT N'CATALOG_ONLY',m.MachineId,N'no_records_in_period',0,0,0,0 FROM #Machine m
WHERE NOT EXISTS(SELECT 1 FROM tx WHERE tx.machine=m.MachineId)
ORDER BY machine,record_type;
"""
    hf=['source_state','status_code','source_rows']
    history=''.join(stage(n,True) for n in ['Patient','Appointment'])+'CREATE INDEX ix_preflight_appt ON #Appointment(DimActivityTransactionID);\n'+stage('History',True)+"""
SELECT N'AVAILABLE' AS source_state,h.ScheduledActivityCode AS status_code,COUNT_BIG(*) AS source_rows
FROM #History h WHERE EXISTS(SELECT 1 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 WHERE a.DimActivityTransactionID=h.DimActivityTransactionID)
GROUP BY h.ScheduledActivityCode ORDER BY h.ScheduledActivityCode;
"""
    cf=['source_state','appointment_status','completion_candidates','appointments',
        'with_activity_end','mean_first_completion_minus_activity_end_seconds']
    completion=''.join(stage(n,True) for n in ['Patient','Appointment'])+'CREATE INDEX ix_completion_appt ON #Appointment(DimActivityTransactionID);\n'+stage('History',True)+"""
;WITH anchors AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,
 MAX(a.ActivityEndDateTime) AS activity_end,
 COUNT(DISTINCT h.ScheduledActivityHstryDateTime) AS candidates,
 MIN(h.ScheduledActivityHstryDateTime) AS first_completion
 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #History h ON h.DimActivityTransactionID=a.DimActivityTransactionID
  AND UPPER(h.ScheduledActivityCode) IN (N'COMPLETED',N'MANUALLY COMPLETED',N'COMPLTFINISH',N'PT. COMPLTFINISH')
  AND h.ScheduledActivityHstryDateTime>=COALESCE(a.ActivityStartDateTime,a.AppointmentDateTime)
  AND h.ScheduledActivityHstryDateTime<DATEADD(hour,12,a.AppointmentDateTime)
 WHERE COALESCE(a.IsScheduled,N'Y')=N'Y' AND COALESCE(a.AppointmentResourceStatus,N'')<>N'Deleted'
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus
)
SELECT N'AVAILABLE' AS source_state,AppointmentStatus AS appointment_status,candidates AS completion_candidates,
 COUNT_BIG(*) AS appointments,SUM(CASE WHEN activity_end IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_end,
 AVG(CAST(DATEDIFF(second,activity_end,first_completion) AS float)) AS mean_first_completion_minus_activity_end_seconds
FROM anchors GROUP BY AppointmentStatus,candidates ORDER BY AppointmentStatus,candidates;
"""
    vf=['source_state','component','version_or_source','interpretation']
    versions="""SET NOCOUNT ON;
SELECT N'TESTED' AS source_state,N'ARIA-DWH' AS component,N'18' AS version_or_source,
 N'Bisher gegen ARIA 18 geprueft; keine automatische Versionsgarantie' AS interpretation
UNION ALL SELECT N'AVAILABLE',N'SQL Server',CONVERT(nvarchar(255),SERVERPROPERTY('ProductVersion')),
 N'SQL-Version, nicht ARIA-Version'
UNION ALL SELECT N'NOT_DETECTED',N'Installierte ARIA-Version',N'',
 N'Bei Abweichung oder Rueckfragen optional im Standortformular angeben'
UNION ALL SELECT N'SCHEMA_CANDIDATE',N'Versionsmetadaten',s.name+N'.'+t.name+N'.'+c.name,
 N'Nur Spaltennachweis; kein als ARIA-Version interpretierter Wert'
FROM sys.objects t JOIN sys.schemas s ON s.schema_id=t.schema_id JOIN sys.columns c ON c.object_id=t.object_id
WHERE t.type IN ('U','V') AND s.name=N'DWH' AND (c.name LIKE N'%Version%' OR t.name LIKE N'%Version%');
"""
    return {
        'AppointmentInventory':(guarded(['Patient','Activity','Machine','Appointment'],af,appointment),af),
        'MachineInventory':(guarded(['Patient','Machine','Treatment'],mf,machine),mf),
        'HistoryStatusInventory':(guarded(['Patient','Appointment'],hf,history),hf),
        'CompletionDiagnostics':(guarded(['Patient','Appointment'],cf,completion),cf),
        'VersionInfo':(versions,vf)}


def create():
    base=build(include_inventory=False);root=ET.parse(base).getroot();uri=NS['r'];tag=lambda s:'{'+uri+'}'+s
    params=root.find('r:ReportParameters',NS)
    for p in params:
        if p.get('Name')=='PeriodEnd':p.find('r:DefaultValue/r:Values/r:Value',NS).text='=DateSerial(2025, 2, 28)'
        if p.get('Name')=='PeriodReason':p.find('r:DefaultValue/r:Values/r:Value',NS).text='Technischer Preflight Januar/Februar 2025'
        if p.get('Name')=='IncludePseudonymizedDetails':
            p.find('r:DefaultValue/r:Values/r:Value',NS).text='false'
            prompt=p.find('r:Prompt',NS)
            if prompt is not None:p.remove(prompt)
            if p.find('r:Hidden',NS) is None:ET.SubElement(p,tag('Hidden')).text='true'
    sets=root.find('r:DataSets',NS)
    sets.remove(next(ds for ds in sets if ds.get('Name')=='EventDetails'))
    catalog=next(ds for ds in sets if ds.get('Name')=='ActivityCatalog')
    catalog_query=catalog.find('r:Query/r:CommandText',NS)
    catalog_query.text=guarded(['Activity'],['activity_code','activity_name','activity_category'],catalog_query.text)
    items=root.find('r:ReportSections/r:ReportSection/r:Body/r:ReportItems',NS)
    for item in list(items):
        if item.findtext('r:DataSetName',namespaces=NS)=='EventDetails':items.remove(item)
    for textbox in items.findall('r:Textbox',NS):
        if textbox.get('Name')=='Title':textbox.find('.//r:Value',NS).text='ARIA Standort-Preflight 2.0'
        if textbox.get('Name')=='Note':textbox.find('.//r:Value',NS).text='Nur Metadaten und aggregierte Konventions-/Quellenpruefung. Keine Patientenlisten. Statusgruppen koennen denselben Termin enthalten; Inventarwerte sind keine klinischen Kennzahlen. Lokal pruefen; nur geschuetzt zur Konfiguration zurueckgeben.'
    top=80
    for i,(name,(sql,fields)) in enumerate(queries().items()):
        ds=ET.SubElement(sets,tag('DataSet'),Name=name);q=ET.SubElement(ds,tag('Query'))
        ET.SubElement(q,tag('DataSourceName')).text='DataSource1'
        qp=ET.SubElement(q,tag('QueryParameters'))
        for par in ['PeriodStart','PeriodEnd']:
            node=ET.SubElement(qp,tag('QueryParameter'),Name='@'+par);ET.SubElement(node,tag('Value')).text='=Parameters!'+par+'.Value'
        ET.SubElement(q,tag('CommandText')).text=sql;ET.SubElement(q,tag('Timeout')).text='180'
        fs=ET.SubElement(ds,tag('Fields'))
        for f in fields:
            node=ET.SubElement(fs,tag('Field'),Name=f);ET.SubElement(node,tag('DataField')).text=f
        layout.FIELDS[name]=fields;layout.PAGE_NAMES[name]=str(i+3).zfill(2)+'_'+name;layout.CAPTIONS[name]=name
        table,top=layout._tablix(name,top);wrapper=ET.fromstring('<root xmlns="'+uri+'">'+table+'</root>');items.append(wrapper[0])
    # Sequential positioning also applies to the inherited metadata tablixes.
    top=40
    for table in items.findall('r:Tablix',NS):
        table.find('r:Top',NS).text=str(top)+'mm';top+=35
    root.find('r:ReportSections/r:ReportSection/r:Body/r:Height',NS).text=str(top)+'mm'
    for prop in root.findall('r:CustomProperties/r:CustomProperty',NS):
        if prop.findtext('r:Name',namespaces=NS)=='ReportName':prop.find('r:Value',NS).text='ARIA18_Standort_Preflight_2.0'
    ET.register_namespace('',uri);ET.register_namespace('rd','http://schemas.microsoft.com/SQLServer/reporting/reportdesigner')
    ET.register_namespace('df','http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition/defaultfontfamily')
    target=base.with_name('ARIA18_Standort_Preflight_2.0.rdl');ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
    build()
    return target


if __name__=='__main__':print(create())
