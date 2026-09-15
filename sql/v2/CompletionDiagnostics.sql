SET NOCOUNT ON;
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL
BEGIN SELECT N'SOURCE_UNAVAILABLE' AS [source_state], CAST(NULL AS nvarchar(255)) AS [appointment_status], CAST(NULL AS nvarchar(255)) AS [completion_candidates], CAST(NULL AS nvarchar(255)) AS [appointments], CAST(NULL AS nvarchar(255)) AS [with_activity_end], CAST(NULL AS nvarchar(255)) AS [mean_first_completion_minus_activity_end_seconds]; RETURN; END;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL, [PatientId] nvarchar(255) NULL, [PatientLastName] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientLastName') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientLastName])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Appointment ([DimActivityTransactionID] bigint NULL, [DimPatientID] bigint NULL, [DimActivityID] bigint NULL, [AppointmentDateTime] datetime2 NULL, [ScheduledEndTime] datetime2 NULL, [ActivityStartDateTime] datetime2 NULL, [ActivityEndDateTime] datetime2 NULL, [AppointmentStatus] nvarchar(255) NULL, [DerivedAppointmentTaskDate] datetime2 NULL, [AppointmentResourceStatus] nvarchar(255) NULL, [IsScheduled] nvarchar(50) NULL, [ctrResourceSer] bigint NULL, [DimResourceID] bigint NULL);
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityTransactionID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentDateTime', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentStatus', 1;
IF OBJECT_ID(N'DWH.DimActivityTransaction') IS NOT NULL
BEGIN
DECLARE @sql_Appointment nvarchar(max) = N'INSERT INTO #Appointment SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(datetime2, s.[AppointmentDateTime])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ScheduledEndTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledEndTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityStartDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityStartDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityEndDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityEndDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + N'TRY_CONVERT(nvarchar(255), s.[AppointmentStatus])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'DerivedAppointmentTaskDate') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[DerivedAppointmentTaskDate])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentResourceStatus') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[AppointmentResourceStatus])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'IsScheduled') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(50), s.[IsScheduled])' ELSE N'CAST(NULL AS nvarchar(50))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ctrResourceSer') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[ctrResourceSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'DimResourceID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimResourceID])' ELSE N'CAST(NULL AS bigint)' END + N' FROM DWH.DimActivityTransaction s WHERE s.AppointmentDateTime>=@context AND s.AppointmentDateTime<DATEADD(day,1,@through)';
EXEC sys.sp_executesql @sql_Appointment, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE INDEX ix_completion_appt ON #Appointment(DimActivityTransactionID);
CREATE TABLE #History ([DimActivityTransactionID] bigint NULL, [ScheduledActivityHstryDateTime] datetime2 NULL, [ScheduledActivityCode] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.DimActivityTransactionHistory') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL
BEGIN
DECLARE @sql_History nvarchar(max) = N'INSERT INTO #History SELECT ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledActivityHstryDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[ScheduledActivityCode])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimActivityTransactionHistory s WHERE EXISTS(SELECT 1 FROM #Appointment a WHERE a.DimActivityTransactionID=s.DimActivityTransactionID) AND s.ScheduledActivityHstryDateTime >= @context AND s.ScheduledActivityHstryDateTime < DATEADD(day,2,@through)';
EXEC sys.sp_executesql @sql_History, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;

;WITH anchors AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,
 MAX(a.ActivityEndDateTime) AS activity_end,
 COUNT(DISTINCT h.ScheduledActivityHstryDateTime) AS candidates,
 MIN(h.ScheduledActivityHstryDateTime) AS first_completion
 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #History h ON h.DimActivityTransactionID=a.DimActivityTransactionID
  AND UPPER(h.ScheduledActivityCode) IN (N'COMPLETED',N'MANUALLY COMPLETED',N'COMPLTFINISH',N'PT. COMPLTFINISH')
  AND h.ScheduledActivityHstryDateTime>=COALESCE(a.ActivityStartDateTime,a.AppointmentDateTime)
  AND h.ScheduledActivityHstryDateTime<DATEADD(hour,12,a.AppointmentDateTime)
 WHERE COALESCE(a.IsScheduled,N'Y')=N'Y' AND COALESCE(a.AppointmentResourceStatus,N'')<>N'Deleted'
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus
)
SELECT N'AVAILABLE' AS source_state,AppointmentStatus AS appointment_status,candidates AS completion_candidates,
 COUNT_BIG(*) AS appointments,SUM(CASE WHEN activity_end IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_end,
 AVG(CAST(DATEDIFF(second,activity_end,first_completion) AS float)) AS mean_first_completion_minus_activity_end_seconds
FROM anchors GROUP BY AppointmentStatus,candidates ORDER BY AppointmentStatus,candidates;
