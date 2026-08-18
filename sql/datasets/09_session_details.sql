WITH {{SESSION_BASE}},
primary_diagnosis AS (
    SELECT fcd.DimCourseID,
           COALESCE(NULLIF(dc.DiagnosisCode, N''), N'OHNE') AS diagnosis_code,
           ROW_NUMBER() OVER (PARTITION BY fcd.DimCourseID
                              ORDER BY ISNULL(fcd.IsPrimary, 0) DESC, fcd.FactCourseDiagnosisID) AS diagnosis_rank
    FROM DWH.FactCourseDiagnosis fcd
    LEFT JOIN DWH.DimDiagnosisCode dc ON dc.DimDiagnosisCodeID = fcd.DimDiagnosisCodeID
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'SessionDetails' AS RecordType,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':PAT:', s.DimPatientID)), 2) AS patient_key,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':COURSE:', s.DimPatientID, N':', s.DimCourseID)), 2) AS course_key,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':PLAN:', s.DimPatientID, N':', s.DimCourseID, N':', s.DimPlanID)), 2) AS plan_key,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':SESSION:', s.DimPatientID, N':', s.machine, N':', CONVERT(varchar(33), s.session_start, 126))), 2) AS session_key,
    s.service_date,
    s.machine,
    s.fraction_number,
    s.planned_fractions,
    s.technique,
    s.treatment_mode,
    CASE WHEN p.diagnosis_code = N'OHNE' THEN N'OHNE'
         ELSE LEFT(UPPER(REPLACE(p.diagnosis_code, N'.', N'')), 3) END AS diagnosis_group,
    s.session_start,
    s.session_end,
    CAST(s.actual_minutes AS decimal(10,2)) AS actual_minutes,
    s.first_imaging_timestamp,
    s.first_beam_timestamp,
    s.clinical_start_timestamp,
    CAST(s.imaging_to_beam_minutes AS decimal(10,2)) AS imaging_to_beam_minutes,
    CAST(s.clinical_span_minutes AS decimal(10,2)) AS clinical_span_minutes,
    s.image_record_count,
    s.image_field_count,
    s.imaging_after_beam_flag,
    s.field_count
FROM session_metrics s
LEFT JOIN primary_diagnosis p ON p.DimCourseID = s.DimCourseID AND p.diagnosis_rank = 1
WHERE @IncludePseudonymizedDetails = 1
  AND s.machine IN (@Machines)
ORDER BY s.service_date, s.machine, s.session_start;
