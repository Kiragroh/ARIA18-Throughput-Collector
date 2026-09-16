SET NOCOUNT ON; IF NOT (COL_LENGTH(N'dbo.ScheduledActivity',N'ScheduledActivitySer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ScheduledActivity',N'OBJECT',N'SELECT',N'ScheduledActivitySer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.ScheduledActivity',N'PatientSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ScheduledActivity',N'OBJECT',N'SELECT',N'PatientSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.ScheduledActivity',N'ScheduledStartTime') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ScheduledActivity',N'OBJECT',N'SELECT',N'ScheduledStartTime',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.ScheduledActivity',N'ActualStartDate') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ScheduledActivity',N'OBJECT',N'SELECT',N'ActualStartDate',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocation',N'ScheduledActivitySer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocation',N'OBJECT',N'SELECT',N'ScheduledActivitySer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocation',N'CheckedInFlag') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocation',N'OBJECT',N'SELECT',N'CheckedInFlag',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocation',N'ArrivalDateTime') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocation',N'OBJECT',N'SELECT',N'ArrivalDateTime',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocationMH',N'ScheduledActivitySer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocationMH',N'OBJECT',N'SELECT',N'ScheduledActivitySer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocationMH',N'CheckedInFlag') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocationMH',N'OBJECT',N'SELECT',N'CheckedInFlag',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.PatientLocationMH',N'ArrivalDateTime') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.PatientLocationMH',N'OBJECT',N'SELECT',N'ArrivalDateTime',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Patient',N'PatientSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Patient',N'OBJECT',N'SELECT',N'PatientSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Patient',N'FirstName') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Patient',N'OBJECT',N'SELECT',N'FirstName',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Patient',N'LastName') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Patient',N'OBJECT',N'SELECT',N'LastName',N'COLUMN'),0)=1) BEGIN SELECT N'UNAVAILABLE' AS source_state,CAST(NULL AS nvarchar(7)) AS period,CAST(NULL AS nvarchar(32)) AS cohort,CAST(NULL AS nvarchar(32)) AS quality,CAST(NULL AS int) AS appointments,CAST(NULL AS int) AS patients,CAST(NULL AS float) AS median_minutes; RETURN; END; BEGIN TRY DECLARE @sql nvarchar(max)=N'
SELECT s.ScheduledActivitySer,s.PatientSer,s.ScheduledStartTime,s.ActualStartDate,
 CASE WHEN UPPER(p.FirstName) LIKE N''%TEST%'' OR UPPER(p.LastName) LIKE N''%TEST%''
 OR UPPER(p.FirstName) LIKE N''%DUMMY%'' OR UPPER(p.LastName) LIKE N''%DUMMY%''
 THEN N''TEST_HINT'' ELSE N''NOT_FLAGGED'' END AS cohort
INTO #waiting_slots FROM dbo.ScheduledActivity s
LEFT JOIN dbo.Patient p ON p.PatientSer=s.PatientSer
WHERE s.ScheduledStartTime>=@a AND s.ScheduledStartTime<DATEADD(day,1,@b);
;WITH arrivals AS (
 SELECT l.ScheduledActivitySer,l.ArrivalDateTime FROM dbo.PatientLocation l
 JOIN #waiting_slots s ON s.ScheduledActivitySer=l.ScheduledActivitySer
 WHERE l.CheckedInFlag=1 AND l.ArrivalDateTime IS NOT NULL
 UNION
 SELECT l.ScheduledActivitySer,l.ArrivalDateTime FROM dbo.PatientLocationMH l
 JOIN #waiting_slots s ON s.ScheduledActivitySer=l.ScheduledActivitySer
 WHERE l.CheckedInFlag=1 AND l.ArrivalDateTime IS NOT NULL
), first_arrival AS (
 SELECT ScheduledActivitySer,MIN(ArrivalDateTime) AS arrival FROM arrivals GROUP BY ScheduledActivitySer
), classified AS (
 SELECT CONVERT(char(7),s.ScheduledStartTime,126) AS period,s.cohort,s.PatientSer,
 CASE WHEN a.arrival IS NULL THEN N''NO_CHECKIN''
 WHEN s.ActualStartDate IS NULL THEN N''NO_ACTUAL_START''
 WHEN s.ActualStartDate<a.arrival THEN N''NEGATIVE''
 WHEN CONVERT(date,a.arrival)<>CONVERT(date,s.ActualStartDate) THEN N''CROSS_DAY''
 WHEN DATEDIFF(second,a.arrival,s.ActualStartDate)>14400 THEN N''OVER_240_MIN''
 ELSE N''SAME_DAY_0_240_MIN'' END AS quality,
 DATEDIFF(second,a.arrival,s.ActualStartDate)/60.0 AS minutes
 FROM #waiting_slots s LEFT JOIN first_arrival a ON a.ScheduledActivitySer=s.ScheduledActivitySer
), quantiles AS (
 SELECT *,PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY minutes)
 OVER (PARTITION BY period,cohort,quality) AS median_minutes FROM classified
)
SELECT N''AVAILABLE'' AS source_state,period,cohort,quality,
 CASE WHEN COUNT(DISTINCT PatientSer)>=5 THEN COUNT(*) END AS appointments,
 CASE WHEN COUNT(DISTINCT PatientSer)>=5 THEN COUNT(DISTINCT PatientSer) END AS patients,
 CASE WHEN COUNT(DISTINCT PatientSer)>=5 AND quality=N''SAME_DAY_0_240_MIN'' AND cohort=N''NOT_FLAGGED''
 THEN MAX(median_minutes) END AS median_minutes
FROM quantiles GROUP BY period,cohort,quality ORDER BY period,cohort,quality;
'; EXEC sys.sp_executesql @sql,N'@a date,@b date',@a=@PeriodStart,@b=@PeriodEnd; END TRY BEGIN CATCH SELECT N'UNAVAILABLE' AS source_state,CAST(NULL AS nvarchar(7)) AS period,CAST(NULL AS nvarchar(32)) AS cohort,CAST(NULL AS nvarchar(32)) AS quality,CAST(NULL AS int) AS appointments,CAST(NULL AS int) AS patients,CAST(NULL AS float) AS median_minutes; END CATCH;