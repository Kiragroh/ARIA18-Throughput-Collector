WITH {{SESSION_BASE}},
primary_diagnosis AS (
    SELECT
        fcd.DimCourseID,
        COALESCE(NULLIF(dc.DiagnosisCode, N''), N'OHNE') AS diagnosis_code,
        COALESCE(NULLIF(dc.DiagnosisClinicalDescriptionDEU, N''), N'Ohne Diagnosezuordnung') AS diagnosis_label,
        ROW_NUMBER() OVER (
            PARTITION BY fcd.DimCourseID
            ORDER BY ISNULL(fcd.IsPrimary, 0) DESC, fcd.FactCourseDiagnosisID
        ) AS diagnosis_rank
    FROM DWH.FactCourseDiagnosis fcd
    LEFT JOIN DWH.DimDiagnosisCode dc ON dc.DimDiagnosisCodeID = fcd.DimDiagnosisCodeID
),
cases AS (
    SELECT
        s.*,
        DATEFROMPARTS(YEAR(s.service_date), MONTH(s.service_date), 1) AS period_month,
        CASE WHEN p.diagnosis_code = N'OHNE' THEN N'OHNE'
             ELSE LEFT(UPPER(REPLACE(p.diagnosis_code, N'.', N'')), 3) END AS diagnosis_group,
        COALESCE(p.diagnosis_label, N'Ohne Diagnosezuordnung') AS diagnosis_label,
        CASE
            WHEN s.planned_fractions = 1 THEN N'01 Fx'
            WHEN s.planned_fractions BETWEEN 2 AND 5 THEN N'02-05 Fx'
            WHEN s.planned_fractions BETWEEN 6 AND 10 THEN N'06-10 Fx'
            WHEN s.planned_fractions BETWEEN 11 AND 20 THEN N'11-20 Fx'
            WHEN s.planned_fractions > 20 THEN N'>20 Fx'
            ELSE N'Fx unbekannt'
        END AS fraction_band
    FROM session_metrics s
    LEFT JOIN primary_diagnosis p
      ON p.DimCourseID = s.DimCourseID AND p.diagnosis_rank = 1
    WHERE s.machine IN (@Machines)
),
dimensions AS (
    SELECT N'Diagnose' AS dimension_name, period_month, machine,
           diagnosis_group AS group_code, MAX(diagnosis_label) AS group_label,
           COUNT_BIG(*) AS delivered_sessions, COUNT(DISTINCT DimPatientID) AS patients,
           AVG(actual_minutes) AS avg_actual_minutes
    FROM cases
    GROUP BY period_month, machine, diagnosis_group
    HAVING COUNT(DISTINCT DimPatientID) >= @MinimumGroupPatients
    UNION ALL
    SELECT N'Fraktionierung', period_month, machine, fraction_band, fraction_band,
           COUNT_BIG(*), COUNT(DISTINCT DimPatientID), AVG(actual_minutes)
    FROM cases
    GROUP BY period_month, machine, fraction_band
    HAVING COUNT(DISTINCT DimPatientID) >= @MinimumGroupPatients
    UNION ALL
    SELECT N'Technik', period_month, machine, technique, technique,
           COUNT_BIG(*), COUNT(DISTINCT DimPatientID), AVG(actual_minutes)
    FROM cases
    GROUP BY period_month, machine, technique
    HAVING COUNT(DISTINCT DimPatientID) >= @MinimumGroupPatients
    UNION ALL
    SELECT N'Adaptivitaet', period_month, machine, treatment_mode, treatment_mode,
           COUNT_BIG(*), COUNT(DISTINCT DimPatientID), AVG(actual_minutes)
    FROM cases
    GROUP BY period_month, machine, treatment_mode
    HAVING COUNT(DISTINCT DimPatientID) >= @MinimumGroupPatients
)
SELECT @MethodVersion AS MethodVersion, @RunId AS RunId, @SiteLabel AS SiteLabel,
       N'CaseMix' AS RecordType, dimension_name, period_month, machine,
       group_code, group_label, delivered_sessions, patients,
       CAST(avg_actual_minutes AS decimal(10,2)) AS avg_actual_minutes
FROM dimensions
ORDER BY dimension_name, period_month, machine, delivered_sessions DESC;
