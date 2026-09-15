SET NOCOUNT ON;
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL
BEGIN SELECT N'SOURCE_UNAVAILABLE' AS [source_state], CAST(NULL AS nvarchar(255)) AS [status_code], CAST(NULL AS nvarchar(255)) AS [source_rows]; RETURN; END;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL);
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Appointment ([DimActivityTransactionID] bigint NULL, [DimPatientID] bigint NULL, [DimActivityID] bigint NULL, [AppointmentDateTime] datetime2 NULL, [ScheduledEndTime] datetime2 NULL, [ActivityStartDateTime] datetime2 NULL, [ActivityEndDateTime] datetime2 NULL, [AppointmentStatus] nvarchar(255) NULL, [AppointmentResourceStatus] nvarchar(255) NULL, [IsScheduled] nvarchar(50) NULL, [ctrResourceSer] bigint NULL, [DimResourceID] bigint NULL);
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityTransactionID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentDateTime', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentStatus', 1;
IF OBJECT_ID(N'DWH.DimActivityTransaction') IS NOT NULL
BEGIN
DECLARE @sql_Appointment nvarchar(max) = N'INSERT INTO #Appointment SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(datetime2, s.[AppointmentDateTime])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ScheduledEndTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledEndTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityStartDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityStartDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityEndDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityEndDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + N'TRY_CONVERT(nvarchar(255), s.[AppointmentStatus])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentResourceStatus') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[AppointmentResourceStatus])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'IsScheduled') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(50), s.[IsScheduled])' ELSE N'CAST(NULL AS nvarchar(50))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ctrResourceSer') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[ctrResourceSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'DimResourceID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimResourceID])' ELSE N'CAST(NULL AS bigint)' END + N' FROM DWH.DimActivityTransaction s WHERE s.AppointmentDateTime>=@context AND s.AppointmentDateTime<DATEADD(day,1,@through)';
EXEC sys.sp_executesql @sql_Appointment, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE INDEX ix_preflight_appt ON #Appointment(DimActivityTransactionID);
CREATE TABLE #History ([DimActivityTransactionID] bigint NULL, [ScheduledActivityHstryDateTime] datetime2 NULL, [ScheduledActivityCode] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.DimActivityTransactionHistory') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL
BEGIN
DECLARE @sql_History nvarchar(max) = N'INSERT INTO #History SELECT ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledActivityHstryDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[ScheduledActivityCode])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimActivityTransactionHistory s WHERE EXISTS(SELECT 1 FROM #Appointment a WHERE a.DimActivityTransactionID=s.DimActivityTransactionID) AND s.ScheduledActivityHstryDateTime >= @context AND s.ScheduledActivityHstryDateTime < DATEADD(day,2,@through)';
EXEC sys.sp_executesql @sql_History, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;

SELECT N'AVAILABLE' AS source_state,h.ScheduledActivityCode AS status_code,COUNT_BIG(*) AS source_rows
FROM #History h WHERE EXISTS(SELECT 1 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 WHERE a.DimActivityTransactionID=h.DimActivityTransactionID)
GROUP BY h.ScheduledActivityCode ORDER BY h.ScheduledActivityCode;
