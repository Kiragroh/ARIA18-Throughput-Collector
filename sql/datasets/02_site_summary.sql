WITH {{SESSION_BASE}},
included AS (
    SELECT *
    FROM session_metrics
    WHERE machine IN (@Machines)
),
device_days AS (
    SELECT
        service_date,
        machine,
        MIN(session_start) AS first_session,
        MAX(session_end) AS last_session
    FROM included
    GROUP BY service_date, machine
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'SiteSummary' AS RecordType,
    CAST(@PeriodStart AS date) AS requested_period_start,
    CAST(@PeriodEnd AS date) AS requested_period_end,
    MIN(i.service_date) AS observed_first_treatment_date,
    MAX(i.service_date) AS observed_last_treatment_date,
    (SELECT COUNT(DISTINCT value) FROM STRING_SPLIT(REPLACE(REPLACE(@MachineList, N'|', N','), N';', N','), N',')) AS selected_machines,
    COUNT(DISTINCT i.machine) AS active_machines,
    COUNT_BIG(*) AS delivered_sessions,
    COUNT(DISTINCT i.DimPatientID) AS unique_patients,
    COUNT(DISTINCT i.service_date) AS active_calendar_days,
    COUNT(DISTINCT CASE WHEN DATEDIFF(DAY, '19000106', i.service_date) % 7 = 0 THEN i.service_date END) AS active_saturdays,
    (SELECT COUNT_BIG(*) FROM device_days) AS active_device_days,
    CAST((
        SELECT SUM(DATEDIFF(MINUTE, d.first_session, d.last_session)) / 60.0
        FROM device_days d
    ) AS decimal(14,2)) AS gross_device_hours
FROM included i;
