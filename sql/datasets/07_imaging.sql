IF OBJECT_ID(N'DWH.FactTreatmentHistory') IS NULL
   OR COL_LENGTH(N'DWH.FactTreatmentHistory', N'IsImage') IS NULL
BEGIN
    SELECT @MethodVersion AS MethodVersion, @RunId AS RunId, @SiteLabel AS SiteLabel,
           N'Imaging' AS RecordType, CAST(NULL AS date) AS period_month,
           CAST(NULL AS nvarchar(255)) AS machine, CAST(NULL AS nvarchar(50)) AS imaging_type,
           CAST(NULL AS bigint) AS image_count, N'nicht verfuegbar' AS capability_status;
END
ELSE
BEGIN
    SELECT
        @MethodVersion AS MethodVersion,
        @RunId AS RunId,
        @SiteLabel AS SiteLabel,
        N'Imaging' AS RecordType,
        DATEFROMPARTS(YEAR(f.TreatmentRecordDateTime), MONTH(f.TreatmentRecordDateTime), 1) AS period_month,
        COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N''), N'OHNE_GERAET') AS machine,
        CASE
            WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%CBCT%' THEN N'CBCT'
            WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%KV%' THEN N'kV'
            WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%MV%' THEN N'MV'
            ELSE N'Bildgebung sonstige'
        END AS imaging_type,
        COUNT_BIG(*) AS image_count,
        N'verfuegbar' AS capability_status
    FROM DWH.FactTreatmentHistory f
    INNER JOIN DWH.DimPatient p ON p.DimPatientID = f.DimPatientID
    LEFT JOIN DWH.DimMachine am ON am.DimMachineID = f.DimActualMachineID
    LEFT JOIN DWH.DimMachine pm ON pm.DimMachineID = f.DimPlanMachineID
    LEFT JOIN DWH.DimField fi ON fi.DimFieldID = f.DimFieldID
    WHERE f.TreatmentRecordDateTime >= @PeriodStart
      AND f.TreatmentRecordDateTime < DATEADD(DAY, 1, @PeriodEnd)
      AND ISNULL(f.IsImage, 0) = 1
      AND ISNULL(p.IsMOTestPatient, 0) = 0
      AND COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N''), N'OHNE_GERAET') IN (@Machines)
    GROUP BY DATEFROMPARTS(YEAR(f.TreatmentRecordDateTime), MONTH(f.TreatmentRecordDateTime), 1),
             COALESCE(NULLIF(am.MachineId, N''), NULLIF(pm.MachineId, N''), N'OHNE_GERAET'),
             CASE
                WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%CBCT%' THEN N'CBCT'
                WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%KV%' THEN N'kV'
                WHEN UPPER(COALESCE(NULLIF(fi.RadiationId, N''), fi.RadiationName, N'')) LIKE N'%MV%' THEN N'MV'
                ELSE N'Bildgebung sonstige'
             END;
END;
