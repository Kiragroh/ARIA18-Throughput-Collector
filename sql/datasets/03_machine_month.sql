WITH {{SESSION_BASE}},
month_spine AS (
    SELECT DATEFROMPARTS(YEAR(@PeriodStart), MONTH(@PeriodStart), 1) AS period_month
    UNION ALL
    SELECT DATEADD(MONTH, 1, period_month)
    FROM month_spine
    WHERE DATEADD(MONTH, 1, period_month) <= DATEFROMPARTS(YEAR(@PeriodEnd), MONTH(@PeriodEnd), 1)
),
selected_machines AS (
    SELECT DISTINCT machine
    FROM session_metrics
    WHERE machine IN (@Machines)
),
coverage AS (
    SELECT
        DATEFROMPARTS(YEAR(service_date), MONTH(service_date), 1) AS period_month,
        machine,
        COUNT_BIG(*) AS delivered_sessions,
        COUNT(DISTINCT DimPatientID) AS treated_patients,
        COUNT(DISTINCT service_date) AS active_device_days,
        MIN(service_date) AS first_treatment_date,
        MAX(service_date) AS last_treatment_date
    FROM session_metrics
    WHERE machine IN (@Machines)
    GROUP BY DATEFROMPARTS(YEAR(service_date), MONTH(service_date), 1), machine
),
matrix AS (
    SELECT
        m.period_month,
        s.machine,
        ISNULL(c.delivered_sessions, 0) AS delivered_sessions,
        ISNULL(c.treated_patients, 0) AS treated_patients,
        ISNULL(c.active_device_days, 0) AS active_device_days,
        c.first_treatment_date,
        c.last_treatment_date,
        CASE WHEN ISNULL(c.delivered_sessions, 0) > 0 THEN 1 ELSE 0 END AS is_active
    FROM month_spine m
    CROSS JOIN selected_machines s
    LEFT JOIN coverage c ON c.period_month = m.period_month AND c.machine = s.machine
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'MachineMonth' AS RecordType,
    period_month,
    machine,
    delivered_sessions,
    treated_patients,
    active_device_days,
    first_treatment_date,
    last_treatment_date,
    is_active,
    SUM(is_active) OVER (PARTITION BY period_month) AS active_machines
FROM matrix
ORDER BY period_month, machine
OPTION (MAXRECURSION 1200);
