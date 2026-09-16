"""Optional DWH image-object adapter; no raw image labels or identifiers exported."""
FIELDS = ["contract_version", "run_id", "source", "event_key", "patient_key", "course_key",
          "machine", "event_start", "event_end", "status", "activity_code", "patient_class",
          "image_kind", "image_seconds", "image_class_evidence", "image_time_source"]
TABLE = "DWH.FactPatientImage"
REQUIRED = ("DimPatientID", "DimMachineID", "ImageCreationDate")
COLUMNS = {"DimPatientID": "bigint", "DimMachineID": "bigint", "ImageCreationDate": "datetime2",
           "DimCourseID": "bigint", "ctrImageSer": "bigint", "FactPatientImageID": "bigint",
           "ImageId": "nvarchar(255)", "ImageType": "nvarchar(255)", "ExposureTime": "float"}


def missing():
    try:
        from .build_collector_v2 import column_available
    except ImportError:
        from build_collector_v2 import column_available
    columns = [(TABLE,c) for c in REQUIRED] + [
        ("DWH.DimPatient","DimPatientID"),("DWH.DimPatient","IsMOTestPatient"),
        ("DWH.DimMachine","DimMachineID"),("DWH.DimMachine","MachineId")]
    return " OR ".join("NOT "+column_available(table,c) for table,c in columns)


def query():
    try:
        from .build_collector_v2 import stage, lit, column_available
    except ImportError:
        from build_collector_v2 import stage, lit, column_available
    columns = COLUMNS
    expressions = []
    for column, dtype in columns.items():
        present = lit(f"TRY_CONVERT({dtype},s.[{column}])")
        expressions.append(present if column in REQUIRED else
            f"CASE WHEN {column_available(TABLE,column)} THEN {present} ELSE {lit('CAST(NULL AS '+dtype+')')} END")
    result = "SET NOCOUNT ON;\nIF @IncludePseudonymizedDetails=0 OR " + missing() + "\nBEGIN SELECT " + ",".join(
        f"CAST(NULL AS nvarchar(255)) AS [{f}]" for f in FIELDS) + " WHERE 1=0; RETURN; END;\n"
    result += stage("Patient") + stage("Machine")
    result += "CREATE TABLE #Images(" + ",".join(f"[{c}] {t} NULL" for c,t in columns.items()) + ");\n"
    result += "DECLARE @image_sql nvarchar(max)=N'INSERT INTO #Images SELECT ' + " + " + N', ' + ".join(expressions)
    result += " + " + lit(f" FROM {TABLE} s WHERE s.ImageCreationDate>=@a AND s.ImageCreationDate<DATEADD(day,1,@b)") + ";\n"
    result += "EXEC sys.sp_executesql @image_sql,N'@a date,@b date',@a=@PeriodStart,@b=@PeriodEnd;\n"
    result += """
;WITH source_objects AS (
 SELECT i.*,COALESCE(m.MachineId,N'') AS machine,
 CASE WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END AS patient_class,
 CASE WHEN ctrImageSer IS NOT NULL THEN CONCAT(N'image:',ctrImageSer)
      WHEN FactPatientImageID IS NOT NULL THEN CONCAT(N'fact:',FactPatientImageID)
      ELSE CONCAT(N'natural:',i.DimPatientID,N':',i.DimMachineID,N':',
          CONVERT(nvarchar(33),ImageCreationDate,126),N':',ImageId,N':',ImageType) END AS object_id,
 CASE WHEN UPPER(COALESCE(ImageType,N''))=N'IMAGEDRR' THEN N'reference'
      WHEN UPPER(CONCAT(ImageId,N' ',ImageType)) LIKE N'%EXACTRAC%' THEN N'exactrac_2d'
      WHEN UPPER(CONCAT(ImageId,N' ',ImageType)) LIKE N'%CBCT%' THEN
        CASE WHEN UPPER(ImageId) LIKE N'KV%' THEN N'kv_cbct'
             WHEN UPPER(ImageId) LIKE N'MV%' THEN N'mv_cbct' ELSE N'cbct_unknown' END
      WHEN UPPER(ImageId) LIKE N'KV%' THEN N'kv_2d'
      WHEN UPPER(ImageId) LIKE N'MV%' THEN N'mv_2d'
      WHEN UPPER(ImageType)=N'IMAGEPI' THEN N'unknown_2d' ELSE N'unknown' END AS image_kind
 FROM #Images i JOIN #Patient p ON p.DimPatientID=i.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #Machine m ON m.DimMachineID=i.DimMachineID
 WHERE i.DimPatientID>0
), objects AS (
 SELECT object_id,DimPatientID,
 CASE WHEN COUNT(DISTINCT DimCourseID)=1 THEN MIN(DimCourseID) END AS DimCourseID,
 CASE WHEN COUNT(DISTINCT machine)=1 THEN MIN(machine) ELSE N'AMBIGUOUS_DEVICE' END AS machine,
 MIN(ImageCreationDate) AS created,
 CASE WHEN COUNT(DISTINCT image_kind)=1 THEN MIN(image_kind) ELSE N'unknown' END AS image_kind,
 MAX(CASE WHEN ExposureTime BETWEEN 1 AND 3600000 THEN ExposureTime/1000.0 END) AS seconds,
 MAX(patient_class) AS patient_class
 FROM source_objects GROUP BY object_id,DimPatientID
)
SELECT N'2.0' AS contract_version,@RunId AS run_id,N'image_object' AS source,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':I:',object_id)),2) AS event_key,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':P:',DimPatientID)),2) AS patient_key,
 CASE WHEN DimCourseID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':C:',DimCourseID)),2) END AS course_key,
 machine,created AS event_start,created AS event_end,N'recorded' AS status,N'' AS activity_code,
 patient_class,image_kind,seconds AS image_seconds,N'label_rule_not_acquisition_verified' AS image_class_evidence,
 N'image_creation_not_acquisition' AS image_time_source
FROM objects ORDER BY created,machine;
"""
    return result
