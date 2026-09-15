
SET NOCOUNT ON;
SET @PeriodStart=CAST(@PeriodStart AS date);
SET @PeriodEnd=CAST(@PeriodEnd AS date);
SET @ContextStart=CAST(@ContextStart AS date);
SET @DataThrough=CAST(@DataThrough AS date);
IF CAST(@PeriodStart AS date) > CAST(@PeriodEnd AS date) OR @ContextStart > @PeriodStart
  OR @DataThrough < @PeriodEnd OR @DataThrough >= CAST(GETDATE() AS date)
  THROW 51000, N'Invalid period/context/data watermark. Use complete past dates.', 1;
IF DATEDIFF(day,@ContextStart,@DataThrough)>1827
  THROW 51000, N'Context larger than five years: split extraction.', 1;
IF @IncludePseudonymizedDetails=0 OR COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL OR COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentRecordDateTime') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsImage') IS NULL OR COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsBrachy') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL OR COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL OR COL_LENGTH(N'DWH.DimActivity',N'DimActivityID') IS NULL OR COL_LENGTH(N'DWH.DimActivity',N'ActivityCode') IS NULL OR (COL_LENGTH(N'DWH.FactTreatmentHistory',N'DeliveredMU') IS NULL AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'FieldMUActual') IS NULL AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'DoseDelivered') IS NULL)
BEGIN
 SELECT CAST(NULL AS nvarchar(255)) AS [contract_version],CAST(NULL AS nvarchar(255)) AS [run_id],CAST(NULL AS nvarchar(255)) AS [source],CAST(NULL AS nvarchar(255)) AS [event_key],CAST(NULL AS nvarchar(255)) AS [patient_key],CAST(NULL AS nvarchar(255)) AS [course_key],CAST(NULL AS nvarchar(255)) AS [plan_key],CAST(NULL AS nvarchar(255)) AS [machine],CAST(NULL AS datetime2) AS [event_start],CAST(NULL AS datetime2) AS [event_end],CAST(NULL AS nvarchar(255)) AS [fraction],CAST(NULL AS nvarchar(255)) AS [activity_code],CAST(NULL AS nvarchar(255)) AS [status],CAST(NULL AS nvarchar(255)) AS [is_brachy],CAST(NULL AS datetime2) AS [activity_start],CAST(NULL AS datetime2) AS [activity_end],CAST(NULL AS datetime2) AS [completed],CAST(NULL AS nvarchar(255)) AS [time_source],CAST(NULL AS nvarchar(255)) AS [completion_candidates],CAST(NULL AS nvarchar(255)) AS [source_rows],CAST(NULL AS nvarchar(255)) AS [activity_name],CAST(NULL AS nvarchar(255)) AS [activity_category],CAST(NULL AS nvarchar(255)) AS [milestone_time],CAST(NULL AS nvarchar(255)) AS [resource_status],CAST(NULL AS nvarchar(255)) AS [patient_class],CAST(NULL AS nvarchar(255)) AS [planned_fractions],CAST(NULL AS nvarchar(255)) AS [plan_first_treatment],CAST(NULL AS nvarchar(255)) AS [plan_last_treatment] WHERE 1=0;
 RETURN;
END;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL THROW 51001,N'Missing cohort source',1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL THROW 51001,N'Missing cohort source',1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPatientID') IS NULL THROW 51001,N'Missing cohort source',1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentRecordDateTime') IS NULL THROW 51001,N'Missing cohort source',1;
CREATE TABLE #Cohort(patient_id bigint NOT NULL PRIMARY KEY);
DECLARE @cohort_sql nvarchar(max)=N'
 INSERT INTO #Cohort
 SELECT DimPatientID FROM DWH.DimActivityTransaction
 WHERE AppointmentDateTime>=@context AND AppointmentDateTime<DATEADD(day,1,@end) AND DimPatientID>0
 UNION
 SELECT DimPatientID FROM DWH.FactTreatmentHistory
 WHERE TreatmentRecordDateTime>=@context AND TreatmentRecordDateTime<DATEADD(day,1,@end) AND DimPatientID>0';
EXEC sys.sp_executesql @cohort_sql,N'@context date,@end date',@context=@ContextStart,@end=@PeriodEnd;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL, [PatientId] nvarchar(255) NULL, [PatientLastName] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NULL THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPatient',N'PatientLastName') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[PatientLastName])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Machine ([DimMachineID] bigint NULL, [MachineId] nvarchar(255) NULL);
IF COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.DimMachineID', 1;
IF COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NULL THROW 51001, N'Required source unavailable: DWH.DimMachine.MachineId', 1;
IF OBJECT_ID(N'DWH.DimMachine') IS NOT NULL
BEGIN
DECLARE @sql_Machine nvarchar(max) = N'INSERT INTO #Machine SELECT ' + N'TRY_CONVERT(bigint, s.[DimMachineID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[MachineId])' + N' FROM DWH.DimMachine s';
EXEC sys.sp_executesql @sql_Machine, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Treatment ([DimPatientID] bigint NULL, [DimCourseID] bigint NULL, [DimPlanID] bigint NULL, [DimFieldID] bigint NULL, [DimActualMachineID] bigint NULL, [DimPlanMachineID] bigint NULL, [TreatmentRecordDateTime] datetime2 NULL, [TreatmentStartTime] datetime2 NULL, [TreatmentEndTime] datetime2 NULL, [FractionNumber] int NULL, [IsImage] int NULL, [IsBrachy] int NULL, [FractionsPlanned] int NULL, [DeliveredMU] float NULL, [FieldMUActual] float NULL, [DoseDelivered] float NULL);
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.DimPatientID', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentRecordDateTime') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.TreatmentRecordDateTime', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsImage') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.IsImage', 1;
IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'IsBrachy') IS NULL THROW 51001, N'Required source unavailable: DWH.FactTreatmentHistory.IsBrachy', 1;
IF OBJECT_ID(N'DWH.FactTreatmentHistory') IS NOT NULL
BEGIN
DECLARE @sql_Treatment nvarchar(max) = N'INSERT INTO #Treatment SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimCourseID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimCourseID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPlanID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimPlanID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimFieldID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimFieldID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimActualMachineID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimActualMachineID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DimPlanMachineID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimPlanMachineID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + N'TRY_CONVERT(datetime2, s.[TreatmentRecordDateTime])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentStartTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[TreatmentStartTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'TreatmentEndTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[TreatmentEndTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FractionNumber') IS NOT NULL THEN N'TRY_CONVERT(int, s.[FractionNumber])' ELSE N'CAST(NULL AS int)' END + N', ' + N'TRY_CONVERT(int, s.[IsImage])' + N', ' + N'TRY_CONVERT(int, s.[IsBrachy])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FractionsPlanned') IS NOT NULL THEN N'TRY_CONVERT(int, s.[FractionsPlanned])' ELSE N'CAST(NULL AS int)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DeliveredMU') IS NOT NULL THEN N'TRY_CONVERT(float, s.[DeliveredMU])' ELSE N'CAST(NULL AS float)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'FieldMUActual') IS NOT NULL THEN N'TRY_CONVERT(float, s.[FieldMUActual])' ELSE N'CAST(NULL AS float)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.FactTreatmentHistory',N'DoseDelivered') IS NOT NULL THEN N'TRY_CONVERT(float, s.[DoseDelivered])' ELSE N'CAST(NULL AS float)' END + N' FROM DWH.FactTreatmentHistory s WHERE s.TreatmentRecordDateTime >= @context AND s.TreatmentRecordDateTime < DATEADD(day,1,@through) AND EXISTS(SELECT 1 FROM #Cohort c WHERE c.patient_id=s.DimPatientID)';
EXEC sys.sp_executesql @sql_Treatment, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Plan ([DimPlanID] bigint NULL, [NoFractionsPlanned] int NULL, [FirstDayOfTreatment] datetime2 NULL, [LastDayOfTreatment] datetime2 NULL);

IF OBJECT_ID(N'DWH.DimPlan') IS NOT NULL AND COL_LENGTH(N'DWH.DimPlan',N'DimPlanID') IS NOT NULL
BEGIN
DECLARE @sql_Plan nvarchar(max) = N'INSERT INTO #Plan SELECT ' + CASE WHEN COL_LENGTH(N'DWH.DimPlan',N'DimPlanID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimPlanID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPlan',N'NoFractionsPlanned') IS NOT NULL THEN N'TRY_CONVERT(int, s.[NoFractionsPlanned])' ELSE N'CAST(NULL AS int)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPlan',N'FirstDayOfTreatment') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[FirstDayOfTreatment])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimPlan',N'LastDayOfTreatment') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[LastDayOfTreatment])' ELSE N'CAST(NULL AS datetime2)' END + N' FROM DWH.DimPlan s WHERE EXISTS(SELECT 1 FROM #Treatment t WHERE t.DimPlanID=s.DimPlanID)';
EXEC sys.sp_executesql @sql_Plan, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Appointment ([DimActivityTransactionID] bigint NULL, [DimPatientID] bigint NULL, [DimActivityID] bigint NULL, [AppointmentDateTime] datetime2 NULL, [ScheduledEndTime] datetime2 NULL, [ActivityStartDateTime] datetime2 NULL, [ActivityEndDateTime] datetime2 NULL, [AppointmentStatus] nvarchar(255) NULL, [DerivedAppointmentTaskDate] datetime2 NULL, [AppointmentResourceStatus] nvarchar(255) NULL, [IsScheduled] nvarchar(50) NULL, [ctrResourceSer] bigint NULL, [DimResourceID] bigint NULL);
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityTransactionID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityTransactionID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimPatientID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimPatientID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentDateTime') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentDateTime', 1;
IF COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentStatus') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivityTransaction.AppointmentStatus', 1;
IF OBJECT_ID(N'DWH.DimActivityTransaction') IS NOT NULL
BEGIN
DECLARE @sql_Appointment nvarchar(max) = N'INSERT INTO #Appointment SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(datetime2, s.[AppointmentDateTime])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ScheduledEndTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledEndTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityStartDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityStartDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ActivityEndDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ActivityEndDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + N'TRY_CONVERT(nvarchar(255), s.[AppointmentStatus])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'DerivedAppointmentTaskDate') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[DerivedAppointmentTaskDate])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'AppointmentResourceStatus') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[AppointmentResourceStatus])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'IsScheduled') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(50), s.[IsScheduled])' ELSE N'CAST(NULL AS nvarchar(50))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'ctrResourceSer') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[ctrResourceSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransaction',N'DimResourceID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimResourceID])' ELSE N'CAST(NULL AS bigint)' END + N' FROM DWH.DimActivityTransaction s WHERE s.AppointmentDateTime >= @context AND s.AppointmentDateTime < DATEADD(month,12,DATEADD(day,1,@through)) AND (COALESCE(s.DimPatientID,0)<=0 OR EXISTS(SELECT 1 FROM #Cohort c WHERE c.patient_id=s.DimPatientID))';
EXEC sys.sp_executesql @sql_Appointment, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE INDEX ix_appointment_id ON #Appointment(DimActivityTransactionID);
CREATE TABLE #Activity ([DimActivityID] bigint NULL, [ActivityCode] nvarchar(255) NULL, [ActivityNameDEU] nvarchar(1000) NULL, [ActivityCategoryDEU] nvarchar(1000) NULL);
IF COL_LENGTH(N'DWH.DimActivity',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivity',N'ActivityCode') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.ActivityCode', 1;
IF OBJECT_ID(N'DWH.DimActivity') IS NOT NULL
BEGIN
DECLARE @sql_Activity nvarchar(max) = N'INSERT INTO #Activity SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[ActivityCode])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityNameDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityNameDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityCategoryDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityCategoryDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N' FROM DWH.DimActivity s';
EXEC sys.sp_executesql @sql_Activity, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Resource ([ctrResourceSer] bigint NULL, [ResourceId] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.vv_ResourceInfo') IS NOT NULL
BEGIN
DECLARE @sql_Resource nvarchar(max) = N'INSERT INTO #Resource SELECT ' + CASE WHEN COL_LENGTH(N'DWH.vv_ResourceInfo',N'ctrResourceSer') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[ctrResourceSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.vv_ResourceInfo',N'ResourceId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[ResourceId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.vv_ResourceInfo s';
EXEC sys.sp_executesql @sql_Resource, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #ResourceMachine ([DimResourceID] bigint NULL, [MachineId] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.InSightiveResourceMachine') IS NOT NULL
BEGIN
DECLARE @sql_ResourceMachine nvarchar(max) = N'INSERT INTO #ResourceMachine SELECT ' + CASE WHEN COL_LENGTH(N'DWH.InSightiveResourceMachine',N'DimResourceID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimResourceID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.InSightiveResourceMachine',N'MachineId') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[MachineId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.InSightiveResourceMachine s';
EXEC sys.sp_executesql @sql_ResourceMachine, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #History ([DimActivityTransactionID] bigint NULL, [ScheduledActivityHstryDateTime] datetime2 NULL, [ScheduledActivityCode] nvarchar(255) NULL);

IF OBJECT_ID(N'DWH.DimActivityTransactionHistory') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL AND COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL
BEGIN
DECLARE @sql_History nvarchar(max) = N'INSERT INTO #History SELECT ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'DimActivityTransactionID') IS NOT NULL THEN N'TRY_CONVERT(bigint, s.[DimActivityTransactionID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityHstryDateTime') IS NOT NULL THEN N'TRY_CONVERT(datetime2, s.[ScheduledActivityHstryDateTime])' ELSE N'CAST(NULL AS datetime2)' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivityTransactionHistory',N'ScheduledActivityCode') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(255), s.[ScheduledActivityCode])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimActivityTransactionHistory s WHERE EXISTS(SELECT 1 FROM #Appointment a WHERE a.DimActivityTransactionID=s.DimActivityTransactionID) AND s.ScheduledActivityHstryDateTime >= @context AND s.ScheduledActivityHstryDateTime < DATEADD(day,2,@through)';
EXEC sys.sp_executesql @sql_History, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;

IF COL_LENGTH(N'DWH.FactTreatmentHistory',N'DeliveredMU') IS NULL
 AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'FieldMUActual') IS NULL
 AND COL_LENGTH(N'DWH.FactTreatmentHistory',N'DoseDelivered') IS NULL
 THROW 51001, N'No delivery evidence column available', 1;
CREATE INDEX ix_history_id ON #History(DimActivityTransactionID,ScheduledActivityHstryDateTime);
CREATE INDEX ix_patient_id ON #Patient(DimPatientID);
;WITH plan_info AS (
 SELECT DimPlanID,
 CASE WHEN COUNT(DISTINCT NoFractionsPlanned)=1 THEN MAX(NoFractionsPlanned) END AS planned_fractions,
 MIN(FirstDayOfTreatment) AS first_treatment,MAX(LastDayOfTreatment) AS last_treatment
 FROM #Plan GROUP BY DimPlanID
), resource_map AS (
 SELECT DISTINCT a.DimActivityTransactionID, m.MachineId
 FROM #Appointment a
 JOIN #Resource r ON r.ctrResourceSer=a.ctrResourceSer
 JOIN #Machine m ON m.MachineId=r.ResourceId
 UNION
 SELECT DISTINCT a.DimActivityTransactionID, m.MachineId
 FROM #Appointment a
 JOIN #ResourceMachine r ON r.DimResourceID=a.DimResourceID
 JOIN #Machine m ON m.MachineId=r.MachineId
), appointment_devices AS (
 SELECT a.DimPatientID,a.DimActivityID,a.AppointmentDateTime,
 CASE WHEN COUNT(DISTINCT r.MachineId)=1 THEN MIN(r.MachineId)
      WHEN COUNT(DISTINCT r.MachineId)>1 THEN N'AMBIGUOUS_DEVICE' ELSE N'' END AS machine
 FROM #Appointment a LEFT JOIN resource_map r ON r.DimActivityTransactionID=a.DimActivityTransactionID
 GROUP BY a.DimPatientID,a.DimActivityID,a.AppointmentDateTime
), events AS (
 SELECT
 CASE WHEN t.IsImage=1 THEN N'imaging' ELSE N'delivery' END AS source,
 CONCAT(N'T:',t.DimPatientID,N':',t.DimCourseID,N':',t.DimPlanID,N':',t.DimFieldID,N':',
        COALESCE(t.DimActualMachineID,t.DimPlanMachineID),N':',t.FractionNumber,N':',t.IsImage,N':',
        CONVERT(nvarchar(33),t.TreatmentRecordDateTime,126),N':',
        CONVERT(nvarchar(33),t.TreatmentStartTime,126)) AS identity_key,
 t.DimPatientID,t.DimCourseID,t.DimPlanID,COALESCE(am.MachineId,pm.MachineId,N'') AS machine,
 COALESCE(t.TreatmentStartTime,t.TreatmentRecordDateTime) AS event_start,
 t.TreatmentEndTime AS event_end,t.FractionNumber AS fraction,
 CAST(N'' AS nvarchar(255)) AS activity_code,CAST(N'delivered' AS nvarchar(255)) AS status,
 t.IsBrachy AS is_brachy,CAST(NULL AS datetime2) AS activity_start,
 CAST(NULL AS datetime2) AS activity_end,CAST(NULL AS datetime2) AS completed,
 CASE WHEN t.TreatmentStartTime IS NOT NULL THEN N'measured' ELSE N'record_fallback' END AS time_source,
 CAST(NULL AS int) AS completion_candidates,
 CAST(N'' AS nvarchar(1000)) AS activity_name,CAST(N'' AS nvarchar(1000)) AS activity_category,
 t.TreatmentRecordDateTime AS milestone_time,CAST(N'' AS nvarchar(255)) AS resource_status,
 CASE WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END AS patient_class,
 COALESCE(pl.planned_fractions,t.FractionsPlanned) AS planned_fractions,
 pl.first_treatment AS plan_first_treatment,pl.last_treatment AS plan_last_treatment
 FROM #Treatment t JOIN #Patient p ON p.DimPatientID=t.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #Machine am ON am.DimMachineID=t.DimActualMachineID
 LEFT JOIN #Machine pm ON pm.DimMachineID=t.DimPlanMachineID
 LEFT JOIN plan_info pl ON pl.DimPlanID=t.DimPlanID
 WHERE t.DimPatientID>0 AND (t.IsImage=1 OR COALESCE(t.DeliveredMU,0)>0
                           OR COALESCE(t.FieldMUActual,0)>0 OR COALESCE(t.DoseDelivered,0)>0)
 UNION ALL
 SELECT N'appointment',
 CONCAT(N'A:',a.DimPatientID,N':',a.DimActivityID,N':',CONVERT(nvarchar(33),a.AppointmentDateTime,126)),
 a.DimPatientID,CAST(NULL AS bigint),CAST(NULL AS bigint),COALESCE(r.machine,N''),
 a.AppointmentDateTime,a.ScheduledEndTime,CAST(NULL AS int),act.ActivityCode,
 a.AppointmentStatus,0,
 a.ActivityStartDateTime,a.ActivityEndDateTime,
 h.completed,N'calendar',h.candidate_count,
 act.ActivityNameDEU,act.ActivityCategoryDEU,
 COALESCE(a.DerivedAppointmentTaskDate,a.AppointmentDateTime),a.AppointmentResourceStatus,
 CASE WHEN COALESCE(a.DimPatientID,0)<=0 THEN N'no_patient'
      WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END,
 CAST(NULL AS int),CAST(NULL AS datetime2),CAST(NULL AS datetime2)
 FROM #Appointment a JOIN #Activity act ON act.DimActivityID=a.DimActivityID
 LEFT JOIN #Patient p ON p.DimPatientID=a.DimPatientID
 LEFT JOIN appointment_devices r ON (r.DimPatientID=a.DimPatientID OR (r.DimPatientID IS NULL AND a.DimPatientID IS NULL))
  AND r.DimActivityID=a.DimActivityID AND r.AppointmentDateTime=a.AppointmentDateTime
 OUTER APPLY (
  SELECT MIN(h.ScheduledActivityHstryDateTime) AS completed,COUNT(DISTINCT h.ScheduledActivityHstryDateTime) AS candidate_count
  FROM #History h WHERE h.DimActivityTransactionID=a.DimActivityTransactionID
   AND UPPER(h.ScheduledActivityCode) IN (N'COMPLETED',N'MANUALLY COMPLETED',N'COMPLTFINISH',N'PT. COMPLTFINISH')
   AND h.ScheduledActivityHstryDateTime >= COALESCE(a.ActivityStartDateTime,a.AppointmentDateTime)
   AND h.ScheduledActivityHstryDateTime < DATEADD(hour,12,a.AppointmentDateTime)
 ) h
 WHERE ((a.DimPatientID>0 AND p.IsMOTestPatient=0) OR (COALESCE(a.DimPatientID,0)<=0
   AND a.AppointmentDateTime>=@PeriodStart AND a.AppointmentDateTime<DATEADD(day,1,@PeriodEnd)))
  AND COALESCE(a.IsScheduled,N'Y')=N'Y'
  AND COALESCE(a.AppointmentResourceStatus,N'')<>N'Deleted'
  AND COALESCE(a.AppointmentStatus,N'')<>N'Deleted'
), keyed_events AS (
 SELECT *, CASE WHEN source=N'appointment' THEN identity_key ELSE
  CONCAT(source,N':',DimPatientID,N':',DimCourseID,N':',DimPlanID,N':',machine,N':',
         CONVERT(nvarchar(10),event_start,23),N':',fraction,N':',time_source) END AS compact_key
 FROM events
), grouped_events AS (
 SELECT source,compact_key AS identity_key,DimPatientID,DimCourseID,DimPlanID,machine,
 MIN(event_start) AS event_start,MAX(event_end) AS event_end,fraction,activity_code,status,is_brachy,
 MIN(activity_start) AS activity_start,MAX(activity_end) AS activity_end,
 CASE WHEN COUNT(DISTINCT completed)<=1 THEN MIN(completed) END AS completed,
 time_source,MAX(completion_candidates) AS completion_candidates,COUNT_BIG(*) AS source_rows,
 MAX(activity_name) AS activity_name,MAX(activity_category) AS activity_category,
 MIN(milestone_time) AS milestone_time,MIN(resource_status) AS resource_status,
 MAX(patient_class) AS patient_class,
 CASE WHEN COUNT(DISTINCT planned_fractions)=1 THEN MAX(planned_fractions) END AS planned_fractions,
 MIN(plan_first_treatment) AS plan_first_treatment,MAX(plan_last_treatment) AS plan_last_treatment
 FROM keyed_events
 GROUP BY source,compact_key,DimPatientID,DimCourseID,DimPlanID,machine,fraction,activity_code,status,is_brachy,time_source
)
SELECT N'2.0' AS contract_version,@RunId AS run_id,source,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':E:',identity_key)),2) AS event_key,
 CASE WHEN DimPatientID>0 THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':P:',DimPatientID)),2) END AS patient_key,
 CASE WHEN DimCourseID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':C:',DimCourseID)),2) END AS course_key,
 CASE WHEN DimPlanID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':L:',DimPlanID)),2) END AS plan_key,
 machine,event_start,event_end,fraction,activity_code,status,is_brachy,activity_start,activity_end,
 completed,time_source,completion_candidates,source_rows,
 activity_name,activity_category,milestone_time,resource_status,patient_class,
 planned_fractions,plan_first_treatment,plan_last_treatment
FROM grouped_events
ORDER BY event_start,source;
