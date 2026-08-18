raw_treatment AS (
    SELECT
        fth.DimPatientID,
        fth.DimCourseID,
        fth.DimPlanID,
        COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N''), N'OHNE_GERAET') AS machine,
        CAST(fth.TreatmentRecordDateTime AS date) AS service_date,
        ISNULL(fth.FractionNumber, 0) AS fraction_number,
        ISNULL(NULLIF(pl.RTTreatmentTechnique, N''), N'Unbekannt') AS technique,
        CASE
            WHEN UPPER(ISNULL(pl.PlanSetupId, N'')) LIKE N'%/ADP%'
              OR UPPER(ISNULL(pl.RTTreatmentTechnique, N'')) LIKE N'%ADAPT%'
            THEN N'Adaptiv'
            ELSE N'Nichtadaptiv'
        END AS treatment_mode,
        ISNULL(NULLIF(pl.NoFractionsPlanned, 0), NULLIF(fth.FractionsPlanned, 0)) AS planned_fractions,
        fth.TreatmentRecordDateTime,
        fth.TreatmentStartTime,
        fth.TreatmentEndTime,
        fth.TreatmentTime,
        fth.DimFieldID
    FROM DWH.FactTreatmentHistory fth
    INNER JOIN DWH.DimPlan pl ON pl.DimPlanID = fth.DimPlanID
    INNER JOIN DWH.DimPatient p ON p.DimPatientID = fth.DimPatientID
    LEFT JOIN DWH.DimMachine am ON am.DimMachineID = fth.DimActualMachineID
    LEFT JOIN DWH.DimMachine pm ON pm.DimMachineID = fth.DimPlanMachineID
    WHERE fth.TreatmentRecordDateTime >= @PeriodStart
      AND fth.TreatmentRecordDateTime < DATEADD(DAY, 1, @PeriodEnd)
      AND ISNULL(fth.IsBrachy, 0) = 0
      AND ISNULL(fth.IsImage, 0) = 0
      AND ISNULL(p.IsMOTestPatient, 0) = 0
      AND (
          ISNULL(fth.DeliveredMU, 0) > 0
          OR ISNULL(fth.FieldMUActual, 0) > 0
          OR ISNULL(fth.DoseDelivered, 0) > 0
      )
),
raw_imaging AS (
    SELECT
        fth.DimPatientID,
        fth.DimCourseID,
        fth.DimPlanID,
        COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N''), N'OHNE_GERAET') AS machine,
        CAST(fth.TreatmentRecordDateTime AS date) AS service_date,
        ISNULL(fth.FractionNumber, 0) AS fraction_number,
        COALESCE(fth.TreatmentStartTime, fth.TreatmentRecordDateTime) AS imaging_timestamp,
        fth.DimFieldID
    FROM DWH.FactTreatmentHistory fth
    INNER JOIN DWH.DimPatient p ON p.DimPatientID = fth.DimPatientID
    LEFT JOIN DWH.DimMachine am ON am.DimMachineID = fth.DimActualMachineID
    LEFT JOIN DWH.DimMachine pm ON pm.DimMachineID = fth.DimPlanMachineID
    WHERE fth.TreatmentRecordDateTime >= @PeriodStart
      AND fth.TreatmentRecordDateTime < DATEADD(DAY, 1, @PeriodEnd)
      AND ISNULL(fth.IsBrachy, 0) = 0
      AND ISNULL(fth.IsImage, 0) = 1
      AND ISNULL(p.IsMOTestPatient, 0) = 0
),
imaging_sessions AS (
    SELECT
        DimPatientID,
        DimCourseID,
        DimPlanID,
        machine,
        service_date,
        fraction_number,
        MIN(imaging_timestamp) AS first_imaging_timestamp,
        COUNT_BIG(*) AS image_record_count,
        COUNT(DISTINCT DimFieldID) AS image_field_count
    FROM raw_imaging
    GROUP BY DimPatientID, DimCourseID, DimPlanID, machine, service_date, fraction_number
),
beam_sessions AS (
    SELECT
        DimPatientID,
        DimCourseID,
        DimPlanID,
        machine,
        service_date,
        fraction_number,
        technique,
        treatment_mode,
        planned_fractions,
        MIN(COALESCE(TreatmentStartTime, TreatmentRecordDateTime)) AS session_start,
        MIN(COALESCE(TreatmentStartTime, TreatmentRecordDateTime)) AS first_beam_timestamp,
        MAX(COALESCE(TreatmentEndTime, TreatmentRecordDateTime)) AS session_end,
        SUM(CASE WHEN TreatmentTime BETWEEN 0 AND 86400 THEN TreatmentTime ELSE 0 END) AS treatment_time_raw_sum,
        COUNT(DISTINCT DimFieldID) AS field_count
    FROM raw_treatment
    GROUP BY
        DimPatientID,
        DimCourseID,
        DimPlanID,
        machine,
        service_date,
        fraction_number,
        technique,
        treatment_mode,
        planned_fractions
),
sessions AS (
    SELECT
        s.*,
        i.first_imaging_timestamp,
        CASE
            WHEN i.first_imaging_timestamp IS NOT NULL
             AND i.first_imaging_timestamp <= s.first_beam_timestamp
            THEN i.first_imaging_timestamp
            ELSE s.first_beam_timestamp
        END AS clinical_start_timestamp,
        ISNULL(i.image_record_count, 0) AS image_record_count,
        ISNULL(i.image_field_count, 0) AS image_field_count,
        CASE WHEN i.first_imaging_timestamp > s.first_beam_timestamp THEN 1 ELSE 0 END AS imaging_after_beam_flag,
        CASE WHEN i.first_imaging_timestamp IS NOT NULL
             THEN DATEDIFF(SECOND, i.first_imaging_timestamp, s.first_beam_timestamp) / 60.0 END AS imaging_to_beam_minutes
    FROM beam_sessions s
    LEFT JOIN imaging_sessions i
      ON i.DimPatientID = s.DimPatientID
     AND i.DimCourseID = s.DimCourseID
     AND i.DimPlanID = s.DimPlanID
     AND i.machine = s.machine
     AND i.service_date = s.service_date
     AND i.fraction_number = s.fraction_number
),
session_metrics AS (
    SELECT
        s.*,
        CASE
            WHEN DATEDIFF(SECOND, s.session_start, s.session_end) BETWEEN 1 AND 14400
            THEN DATEDIFF(SECOND, s.session_start, s.session_end) / 60.0
        END AS actual_minutes,
        CASE
            WHEN DATEDIFF(SECOND, s.clinical_start_timestamp, s.session_end) BETWEEN 1 AND 14400
            THEN DATEDIFF(SECOND, s.clinical_start_timestamp, s.session_end) / 60.0
        END AS clinical_span_minutes,
        LEAD(s.session_start) OVER (
            PARTITION BY s.service_date, s.machine
            ORDER BY s.session_start, s.DimPlanID, s.fraction_number
        ) AS next_session_start
    FROM sessions s
)
