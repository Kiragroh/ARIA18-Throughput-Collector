SET NOCOUNT ON;
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentRecordDateTime') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsImage') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsBrachy') IS NULL
BEGIN SELECT N'SOURCE_UNAVAILABLE' AS [source_state], CAST(NULL AS nvarchar(255)) AS [machine], CAST(NULL AS nvarchar(255)) AS [record_type], CAST(NULL AS nvarchar(255)) AS [source_rows], CAST(NULL AS nvarchar(255)) AS [with_technical_start], CAST(NULL AS nvarchar(255)) AS [with_technical_end], CAST(NULL AS nvarchar(255)) AS [with_delivery_evidence]; RETURN; END;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL, [PatientId] nvarchar(255) NULL, [PatientLastName] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientLastName') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientLastName])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Machine ([DimMachineID] bigint NULL, [MachineId] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.DimMachineID', 1;
IF COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.MachineId', 1;
IF OBJECT_ID(N'DWH.DimMachine') IS NOT NULL
BEGIN
DECLARE @sql_Machine nvarchar(max) = N'INSERT INTO #Machine SELECT ' + N'TRY_CONVERT(bigint, s.[DimMachineID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[MachineId])' + N' FROM DWH.DimMachine s';
EXEC sys.sp_executesql @sql_Machine, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Treatment ([DimPatientID] bigint NULL, [DimCourseID] bigint NULL, [DimPlanID] bigint NULL, [DimFieldID] bigint NULL, [DimActualMachineID] bigint NULL, [DimPlanMachineID] bigint NULL, [TreatmentRecordDateTime] datetime2 NULL, [TreatmentStartTime] datetime2 NULL, [TreatmentEndTime] datetime2 NULL, [FractionNumber] int NULL, [IsImage] int NULL, [IsBrachy] int NULL, [FractionsPlanned] int NULL, [DeliveredMU] float NULL, [FieldMUActual] float NULL, [DoseDelivered] float NULL);
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.DimPatientID', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentRecordDateTime') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.TreatmentRecordDateTime', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsImage') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.IsImage', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsBrachy') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.IsBrachy', 1;
IF OBJECT_ID(N'DWH.FactTreatmentHistory') IS NOT NULL
BEGIN
DECLARE @sql_Treatment nvarchar(max) = N'INSERT INTO #Treatment SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimCourseID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimCourseID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPlanID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimPlanID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimFieldID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimFieldID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimActualMachineID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimActualMachineID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPlanMachineID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimPlanMachineID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + N'TRY_CONVERT(datetime2, s.[TreatmentRecordDateTime])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentStartTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[TreatmentStartTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentEndTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[TreatmentEndTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FractionNumber') IS NOT NULL THEN N'TRY_CONVERT(int, s.[FractionNumber])' ELSE N'CAST(NULL AS int)' END + N', ' + N'TRY_CONVERT(int, s.[IsImage])' + N', ' + N'TRY_CONVERT(int, s.[IsBrachy])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FractionsPlanned') IS NOT NULL THEN N'TRY_CONVERT(int, s.[FractionsPlanned])' ELSE N'CAST(NULL AS int)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DeliveredMU') IS NOT NULL THEN N'TRY_CONVERT(float, s.[DeliveredMU])' ELSE N'CAST(NULL AS float)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FieldMUActual') IS NOT NULL THEN N'TRY_CONVERT(float, s.[FieldMUActual])' ELSE N'CAST(NULL AS float)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DoseDelivered') IS NOT NULL THEN N'TRY_CONVERT(float, s.[DoseDelivered])' ELSE N'CAST(NULL AS float)' END + N' FROM DWH.FactTreatmentHistory s WHERE s.TreatmentRecordDateTime>=@context AND s.TreatmentRecordDateTime<DATEADD(day,1,@through)';
EXEC sys.sp_executesql @sql_Treatment, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;

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
