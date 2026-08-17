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
sessions AS (
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
session_metrics AS (
    SELECT
        s.*,
        CASE
            WHEN DATEDIFF(SECOND, s.session_start, s.session_end) BETWEEN 1 AND 14400
            THEN DATEDIFF(SECOND, s.session_start, s.session_end) / 60.0
        END AS actual_minutes,
        LEAD(s.session_start) OVER (
            PARTITION BY s.service_date, s.machine
            ORDER BY s.session_start, s.DimPlanID, s.fraction_number
        ) AS next_session_start
    FROM sessions s
)
