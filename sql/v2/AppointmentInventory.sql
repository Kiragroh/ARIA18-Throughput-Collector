SET NOCOUNT ON;
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL OR COL_LENGTH(N'DWH.DimActivity',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivity',N'ActivityCode') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL
BEGIN SELECT N'SOURCE_UNAVAILABLE' AS [source_state], CAST(NULL AS nvarchar(255)) AS [activity_code], CAST(NULL AS nvarchar(255)) AS [activity_name], CAST(NULL AS nvarchar(255)) AS [appointment_status], CAST(NULL AS nvarchar(255)) AS [machine], CAST(NULL AS nvarchar(255)) AS [distinct_appointments], CAST(NULL AS nvarchar(255)) AS [resource_rows], CAST(NULL AS nvarchar(255)) AS [with_activity_start], CAST(NULL AS nvarchar(255)) AS [with_activity_end], CAST(NULL AS nvarchar(255)) AS [with_calendar_end], CAST(NULL AS nvarchar(255)) AS [plausible_activity_intervals]; RETURN; END;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL, [PatientId] nvarchar(255) NULL, [PatientLastName] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientLastName') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientLastName])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Activity ([DimActivityID] bigint NULL, [ActivityCode] nvarchar(255) NULL, [ActivityNameDEU] nvarchar(1000) NULL, [ActivityCategoryDEU] nvarchar(1000) NULL);
IF COL_LENGTH(N'DWH.DimActivity',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivity',N'ActivityCode') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.ActivityCode', 1;
IF OBJECT_ID(N'DWH.DimActivity') IS NOT NULL
BEGIN
DECLARE @sql_Activity nvarchar(max) = N'INSERT INTO #Activity SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[ActivityCode])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityNameDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityNameDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityCategoryDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityCategoryDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N' FROM DWH.DimActivity s';
EXEC sys.sp_executesql @sql_Activity, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Machine ([DimMachineID] bigint NULL, [MachineId] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.DimMachineID', 1;
IF COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.MachineId', 1;
IF OBJECT_ID(N'DWH.DimMachine') IS NOT NULL
BEGIN
DECLARE @sql_Machine nvarchar(max) = N'INSERT INTO #Machine SELECT ' + N'TRY_CONVERT(bigint, s.[DimMachineID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[MachineId])' + N' FROM DWH.DimMachine s';
EXEC sys.sp_executesql @sql_Machine, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #Resource ([ctrResourceSer] bigint NULL, [ResourceId] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.vv_ResourceInfo') IS NOT NULL
BEGIN
DECLARE @sql_Resource nvarchar(max) = N'INSERT INTO #Resource SELECT ' + CASE WHEN COL_LENGTH(N'DWH.vv_ResourceInfo',N'ctrResourceSer') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[ctrResourceSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.vv_ResourceInfo',N'ResourceId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[ResourceId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.vv_ResourceInfo s';
EXEC sys.sp_executesql @sql_Resource, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
END;
CREATE TABLE #ResourceMachine ([DimResourceID] bigint NULL, [MachineId] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.InSightiveResourceMachine') IS NOT NULL
BEGIN
DECLARE @sql_ResourceMachine nvarchar(max) = N'INSERT INTO #ResourceMachine SELECT ' + CASE WHEN COL_LENGTH(N'DWH.InSightiveResourceMachine',N'DimResourceID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimResourceID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.InSightiveResourceMachine',N'MachineId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[MachineId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.InSightiveResourceMachine s';
EXEC sys.sp_executesql @sql_ResourceMachine, N'@context date,@through date', @context= @PeriodStart, @through= @PeriodEnd;
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

;WITH resources AS (
 SELECT DISTINCT a.DimActivityTransactionID,m.MachineId FROM #Appointment a
 JOIN #Resource r ON r.ctrResourceSer=a.ctrResourceSer JOIN #Machine m ON m.MachineId=r.ResourceId
 UNION
 SELECT DISTINCT a.DimActivityTransactionID,m.MachineId FROM #Appointment a
 JOIN #ResourceMachine r ON r.DimResourceID=a.DimResourceID JOIN #Machine m ON m.MachineId=r.MachineId
), devices AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,
 CASE WHEN COUNT(DISTINCT r.MachineId)=1 THEN MIN(r.MachineId)
      WHEN COUNT(DISTINCT r.MachineId)>1 THEN N'AMBIGUOUS_DEVICE' ELSE N'UNMAPPED' END AS machine
 FROM #Appointment a LEFT JOIN resources r ON r.DimActivityTransactionID=a.DimActivityTransactionID
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime
), appointments AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,d.machine,
 COUNT_BIG(*) AS resource_rows,MAX(a.ActivityStartDateTime) AS activity_start,
 MAX(a.ActivityEndDateTime) AS activity_end,MAX(a.ScheduledEndTime) AS calendar_end
 FROM #Appointment a JOIN #Patient p ON p.DimPatientID=a.DimPatientID AND p.IsMOTestPatient=0
 JOIN devices d ON d.DimPatientID=a.DimPatientID AND d.DimActivityID=a.DimActivityID AND d.AppointmentDateTime=a.AppointmentDateTime
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,a.AppointmentStatus,d.machine
)
SELECT N'AVAILABLE' AS source_state,act.ActivityCode AS activity_code,MAX(act.ActivityNameDEU) AS activity_name,
 a.AppointmentStatus AS appointment_status,a.machine,COUNT_BIG(*) AS distinct_appointments,
 SUM(a.resource_rows) AS resource_rows,SUM(CASE WHEN activity_start IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_start,
 SUM(CASE WHEN activity_end IS NOT NULL THEN 1 ELSE 0 END) AS with_activity_end,
 SUM(CASE WHEN calendar_end IS NOT NULL THEN 1 ELSE 0 END) AS with_calendar_end,
 SUM(CASE WHEN DATEDIFF(second,activity_start,activity_end)>0 AND DATEDIFF(second,activity_start,activity_end)<=14400 THEN 1 ELSE 0 END) AS plausible_activity_intervals
FROM appointments a JOIN #Activity act ON act.DimActivityID=a.DimActivityID
GROUP BY act.ActivityCode,a.AppointmentStatus,a.machine ORDER BY act.ActivityCode,a.machine,a.AppointmentStatus;
