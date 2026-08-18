WITH required_sources AS (
    SELECT N'DWH.FactTreatmentHistory' AS source_name, N'TreatmentRecordDateTime' AS column_name UNION ALL
    SELECT N'DWH.FactTreatmentHistory', N'TreatmentStartTime' UNION ALL
    SELECT N'DWH.FactTreatmentHistory', N'IsImage' UNION ALL
    SELECT N'DWH.DimActivityTransaction', N'AppointmentDateTime' UNION ALL
    SELECT N'DWH.DimActivityTransaction', N'PatientArrivalDateTime' UNION ALL
    SELECT N'DWH.DimActivityTransactionHistory', N'ScheduledActivityHstryDateTime' UNION ALL
    SELECT N'DWH.DimActivityTransactionHistory', N'ScheduledActivityCode' UNION ALL
    SELECT N'DWH.DimActivityTransactionHistory', N'ArrivalDateTime' UNION ALL
    SELECT N'DWH.vv_ResourceInfo', N'ctrResourceSer' UNION ALL
    SELECT N'DWH.InSightiveResourceMachine', N'DimResourceID' UNION ALL
    SELECT N'DWH.FactCourseDiagnosis', N'DimCourseID' UNION ALL
    SELECT N'DWH.DimDiagnosisCode', N'DiagnosisCode'
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'Capabilities' AS RecordType,
    source_name,
    column_name,
    CASE
        WHEN OBJECT_ID(source_name) IS NOT NULL
         AND COL_LENGTH(source_name, column_name) IS NOT NULL
        THEN 1 ELSE 0
    END AS is_available
FROM required_sources
ORDER BY source_name, column_name;
