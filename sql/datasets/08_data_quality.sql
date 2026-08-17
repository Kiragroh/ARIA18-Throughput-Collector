WITH raw_scope AS (
    SELECT f.*, p.IsMOTestPatient,
           COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N'')) AS resolved_machine
    FROM DWH.FactTreatmentHistory f
    INNER JOIN DWH.DimPatient p ON p.DimPatientID = f.DimPatientID
    LEFT JOIN DWH.DimMachine am ON am.DimMachineID = f.DimActualMachineID
    LEFT JOIN DWH.DimMachine pm ON pm.DimMachineID = f.DimPlanMachineID
    WHERE f.TreatmentRecordDateTime >= @PeriodStart
      AND f.TreatmentRecordDateTime < DATEADD(DAY, 1, @PeriodEnd)
),
quality AS (
    SELECT
        COUNT_BIG(*) AS raw_rows,
        SUM(CASE WHEN ISNULL(IsImage, 0) = 1 THEN 1 ELSE 0 END) AS excluded_images,
        SUM(CASE WHEN ISNULL(IsBrachy, 0) = 1 THEN 1 ELSE 0 END) AS excluded_brachy,
        SUM(CASE WHEN ISNULL(IsMOTestPatient, 0) = 1 THEN 1 ELSE 0 END) AS excluded_test_patients,
        SUM(CASE WHEN ISNULL(IsImage, 0) = 0 AND ISNULL(IsBrachy, 0) = 0
                  AND ISNULL(IsMOTestPatient, 0) = 0
                  AND (ISNULL(DeliveredMU, 0) > 0 OR ISNULL(FieldMUActual, 0) > 0 OR ISNULL(DoseDelivered, 0) > 0)
                 THEN 1 ELSE 0 END) AS valid_sessions,
        SUM(CASE WHEN resolved_machine IS NULL THEN 1 ELSE 0 END) AS missing_machine,
        SUM(CASE WHEN FractionNumber IS NULL OR FractionNumber <= 0 THEN 1 ELSE 0 END) AS missing_fraction
    FROM raw_scope
)
SELECT @MethodVersion AS MethodVersion, @RunId AS RunId, @SiteLabel AS SiteLabel,
       N'DataQuality' AS RecordType, raw_rows, excluded_images, excluded_brachy,
       excluded_test_patients, valid_sessions, missing_machine, missing_fraction
FROM quality;
