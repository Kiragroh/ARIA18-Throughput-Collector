IF OBJECT_ID('tempdb..#appointment_source') IS NOT NULL DROP TABLE #appointment_source;

CREATE TABLE #appointment_source (
    appointment_id bigint NOT NULL,
    DimPatientID bigint NULL,
    service_date date NOT NULL,
    machine nvarchar(255) NOT NULL,
    slot_start datetime2 NULL,
    slot_end datetime2 NULL,
    activity_start datetime2 NULL,
    activity_end datetime2 NULL,
    activity_code nvarchar(255) NULL,
    activity_name nvarchar(1000) NULL,
    activity_category nvarchar(1000) NULL,
    scheduled_minutes decimal(12,2) NULL,
    activity_minutes decimal(12,2) NULL,
    mapping_source nvarchar(100) NOT NULL,
    patient_arrival_timestamp datetime2 NULL,
    arrival_source nvarchar(100) NULL,
    appointment_status nvarchar(255) NULL,
    checked_in nvarchar(50) NULL,
    pending_or_in_progress_timestamp datetime2 NULL,
    pending_or_in_progress_status nvarchar(255) NULL,
    completed_timestamp datetime2 NULL,
    completed_status nvarchar(255) NULL
);

DECLARE @resource_sql nvarchar(max);

IF OBJECT_ID(N'DWH.vv_ResourceInfo') IS NOT NULL
   AND COL_LENGTH(N'DWH.DimActivityTransaction', N'ctrResourceSer') IS NOT NULL
BEGIN
    SET @resource_sql = N'
        INSERT INTO #appointment_source
        SELECT DISTINCT
            CONVERT(bigint, at.DimActivityTransactionID),
            CONVERT(bigint, at.DimPatientID),
            CAST(at.AppointmentDateTime AS date),
            COALESCE(NULLIF(r.ResourceId, N''''), NULLIF(r.ResourceFullName, N''''), N''OHNE_RESSOURCE''),
            at.AppointmentDateTime,
            at.ScheduledEndTime,
            at.ActivityStartDateTime,
            at.ActivityEndDateTime,
            a.ActivityCode,
            COALESCE(NULLIF(a.ActivityNameDEU, N''''), NULLIF(a.ActivityCode, N''''), N''Ohne Aktivitaetsbezeichnung''),
            COALESCE(NULLIF(a.ActivityCategoryDEU, N''''), N''Ohne Kategorie''),
            CASE WHEN DATEDIFF(MINUTE, at.AppointmentDateTime, at.ScheduledEndTime) BETWEEN 1 AND 480
                 THEN DATEDIFF(MINUTE, at.AppointmentDateTime, at.ScheduledEndTime) END,
            CASE WHEN DATEDIFF(MINUTE, at.ActivityStartDateTime, at.ActivityEndDateTime) BETWEEN 1 AND 480
                 THEN DATEDIFF(MINUTE, at.ActivityStartDateTime, at.ActivityEndDateTime) END,
            N''vv_ResourceInfo/ctrResourceSer'',
            at.PatientArrivalDateTime,
            CASE WHEN at.PatientArrivalDateTime IS NOT NULL THEN N''DimActivityTransaction.PatientArrivalDateTime'' END,
            at.AppointmentStatus,
            at.CheckedIn,
            NULL, NULL, NULL, NULL
        FROM DWH.DimActivityTransaction at
        INNER JOIN DWH.vv_ResourceInfo r ON r.ctrResourceSer = at.ctrResourceSer
        INNER JOIN DWH.DimActivity a ON a.DimActivityID = at.DimActivityID
        INNER JOIN DWH.DimPatient p ON p.DimPatientID = at.DimPatientID
        WHERE at.AppointmentDateTime >= @p_start
          AND at.AppointmentDateTime < DATEADD(DAY, 1, @p_end)
          AND ISNULL(at.IsScheduled, N''Y'') = N''Y''
          AND ISNULL(at.AppointmentStatus, N'''') NOT LIKE N''%Cancel%''
          AND ISNULL(at.AppointmentStatus, N'''') <> N''Deleted''
          AND ISNULL(at.AppointmentResourceStatus, N''Active'') <> N''Deleted''
          AND at.DimPatientID > 0
          AND ISNULL(p.IsMOTestPatient, 0) = 0;';
END
ELSE IF OBJECT_ID(N'DWH.InSightiveResourceMachine') IS NOT NULL
    AND COL_LENGTH(N'DWH.DimActivityTransaction', N'DimResourceID') IS NOT NULL
BEGIN
    SET @resource_sql = N'
        INSERT INTO #appointment_source
        SELECT DISTINCT
            CONVERT(bigint, at.DimActivityTransactionID),
            CONVERT(bigint, at.DimPatientID),
            CAST(at.AppointmentDateTime AS date),
            COALESCE(NULLIF(r.MachineId, N''''), NULLIF(r.MachineFullName, N''''), N''OHNE_RESSOURCE''),
            at.AppointmentDateTime,
            at.ScheduledEndTime,
            at.ActivityStartDateTime,
            at.ActivityEndDateTime,
            a.ActivityCode,
            COALESCE(NULLIF(a.ActivityNameDEU, N''''), NULLIF(a.ActivityCode, N''''), N''Ohne Aktivitaetsbezeichnung''),
            COALESCE(NULLIF(a.ActivityCategoryDEU, N''''), N''Ohne Kategorie''),
            CASE WHEN DATEDIFF(MINUTE, at.AppointmentDateTime, at.ScheduledEndTime) BETWEEN 1 AND 480
                 THEN DATEDIFF(MINUTE, at.AppointmentDateTime, at.ScheduledEndTime) END,
            CASE WHEN DATEDIFF(MINUTE, at.ActivityStartDateTime, at.ActivityEndDateTime) BETWEEN 1 AND 480
                 THEN DATEDIFF(MINUTE, at.ActivityStartDateTime, at.ActivityEndDateTime) END,
            N''InSightiveResourceMachine/DimResourceID'',
            at.PatientArrivalDateTime,
            CASE WHEN at.PatientArrivalDateTime IS NOT NULL THEN N''DimActivityTransaction.PatientArrivalDateTime'' END,
            at.AppointmentStatus,
            at.CheckedIn,
            NULL, NULL, NULL, NULL
        FROM DWH.DimActivityTransaction at
        INNER JOIN DWH.InSightiveResourceMachine r ON r.DimResourceID = at.DimResourceID
        INNER JOIN DWH.DimActivity a ON a.DimActivityID = at.DimActivityID
        INNER JOIN DWH.DimPatient p ON p.DimPatientID = at.DimPatientID
        WHERE at.AppointmentDateTime >= @p_start
          AND at.AppointmentDateTime < DATEADD(DAY, 1, @p_end)
          AND ISNULL(at.IsScheduled, N''Y'') = N''Y''
          AND ISNULL(at.AppointmentStatus, N'''') NOT LIKE N''%Cancel%''
          AND ISNULL(at.AppointmentStatus, N'''') <> N''Deleted''
          AND ISNULL(at.AppointmentResourceStatus, N''Active'') <> N''Deleted''
          AND at.DimPatientID > 0
          AND ISNULL(p.IsMOTestPatient, 0) = 0;';
END;

IF @resource_sql IS NOT NULL
BEGIN
    EXEC sys.sp_executesql
        @resource_sql,
        N'@p_start date, @p_end date',
        @p_start = @PeriodStart,
        @p_end = @PeriodEnd;
END;

IF OBJECT_ID(N'DWH.DimActivityTransactionHistory') IS NOT NULL
   AND COL_LENGTH(N'DWH.DimActivityTransactionHistory', N'ScheduledActivityHstryDateTime') IS NOT NULL
BEGIN
    ;WITH history_events AS (
        SELECT
            h.DimActivityTransactionID AS appointment_id,
            MIN(h.ArrivalDateTime) AS history_arrival_timestamp,
            MIN(CASE
                WHEN UPPER(LTRIM(RTRIM(ISNULL(h.ScheduledActivityCode, N'')))) IN
                     (N'PENDING', N'IN PROGRESS', N'IN PROGRESS (MANUALLY SET)')
                THEN h.ScheduledActivityHstryDateTime
            END) AS pending_or_in_progress_timestamp,
            MIN(CASE
                WHEN UPPER(LTRIM(RTRIM(ISNULL(h.ScheduledActivityCode, N'')))) IN
                     (N'PENDING', N'IN PROGRESS', N'IN PROGRESS (MANUALLY SET)')
                THEN h.ScheduledActivityCode
            END) AS pending_or_in_progress_status,
            MIN(CASE
                WHEN UPPER(LTRIM(RTRIM(ISNULL(h.ScheduledActivityCode, N'')))) IN
                     (N'COMPLETED', N'MANUALLY COMPLETED')
                THEN h.ScheduledActivityHstryDateTime
            END) AS completed_timestamp,
            MIN(CASE
                WHEN UPPER(LTRIM(RTRIM(ISNULL(h.ScheduledActivityCode, N'')))) IN
                     (N'COMPLETED', N'MANUALLY COMPLETED')
                THEN h.ScheduledActivityCode
            END) AS completed_status
        FROM DWH.DimActivityTransactionHistory h
        INNER JOIN #appointment_source a ON a.appointment_id = h.DimActivityTransactionID
        GROUP BY h.DimActivityTransactionID
    )
    UPDATE a
       SET patient_arrival_timestamp = COALESCE(a.patient_arrival_timestamp, h.history_arrival_timestamp),
           arrival_source = CASE
               WHEN a.patient_arrival_timestamp IS NOT NULL THEN a.arrival_source
               WHEN h.history_arrival_timestamp IS NOT NULL THEN N'DimActivityTransactionHistory.ArrivalDateTime'
           END,
           pending_or_in_progress_timestamp = h.pending_or_in_progress_timestamp,
           pending_or_in_progress_status = h.pending_or_in_progress_status,
           completed_timestamp = h.completed_timestamp,
           completed_status = h.completed_status
    FROM #appointment_source a
    INNER JOIN history_events h ON h.appointment_id = a.appointment_id;
END;
