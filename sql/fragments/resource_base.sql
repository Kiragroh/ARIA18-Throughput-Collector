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
    mapping_source nvarchar(100) NOT NULL
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
            N''vv_ResourceInfo/ctrResourceSer''
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
            N''InSightiveResourceMachine/DimResourceID''
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
