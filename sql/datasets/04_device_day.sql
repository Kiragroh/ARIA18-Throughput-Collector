WITH {{SESSION_BASE}},
enriched AS (
    SELECT
        sm.*,
        CASE
            WHEN DATEDIFF(SECOND, sm.session_start, sm.next_session_start) BETWEEN 60 AND 43200
            THEN DATEDIFF(SECOND, sm.session_start, sm.next_session_start) / 60.0
        END AS cycle_minutes,
        CASE
            WHEN DATEDIFF(SECOND, sm.session_end, sm.next_session_start) BETWEEN 0 AND 43200
            THEN DATEDIFF(SECOND, sm.session_end, sm.next_session_start) / 60.0
        END AS idle_minutes
    FROM session_metrics sm
    WHERE sm.machine IN (@Machines)
),
with_percentiles AS (
    SELECT
        e.*,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY e.actual_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p25_actual_minutes,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.actual_minutes) OVER (PARTITION BY e.service_date, e.machine) AS median_actual_minutes,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY e.actual_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p75_actual_minutes,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY e.actual_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p90_actual_minutes,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY e.cycle_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p25_cycle_minutes,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.cycle_minutes) OVER (PARTITION BY e.service_date, e.machine) AS median_cycle_minutes,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY e.cycle_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p75_cycle_minutes,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY e.cycle_minutes) OVER (PARTITION BY e.service_date, e.machine) AS p90_cycle_minutes
    FROM enriched e
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'DeviceDay' AS RecordType,
    service_date,
    DATENAME(WEEKDAY, service_date) AS weekday_name,
    machine,
    COUNT_BIG(*) AS delivered_sessions,
    COUNT(DISTINCT DimPatientID) AS treated_patients,
    SUM(CASE WHEN fraction_number = 1 THEN 1 ELSE 0 END) AS first_fractions,
    SUM(field_count) AS delivered_fields,
    MIN(session_start) AS first_session,
    MAX(session_end) AS last_session,
    DATEDIFF(MINUTE, MIN(session_start), MAX(session_end)) AS operating_span_minutes,
    CAST(AVG(actual_minutes) AS decimal(10,2)) AS avg_actual_minutes,
    CAST(MAX(median_actual_minutes) AS decimal(10,2)) AS median_actual_minutes,
    CAST(MAX(p25_actual_minutes) AS decimal(10,2)) AS p25_actual_minutes,
    CAST(MAX(p75_actual_minutes) AS decimal(10,2)) AS p75_actual_minutes,
    CAST(MAX(p90_actual_minutes) AS decimal(10,2)) AS p90_actual_minutes,
    CAST(AVG(cycle_minutes) AS decimal(10,2)) AS avg_cycle_minutes,
    CAST(MAX(median_cycle_minutes) AS decimal(10,2)) AS median_cycle_minutes,
    CAST(MAX(p25_cycle_minutes) AS decimal(10,2)) AS p25_cycle_minutes,
    CAST(MAX(p75_cycle_minutes) AS decimal(10,2)) AS p75_cycle_minutes,
    CAST(MAX(p90_cycle_minutes) AS decimal(10,2)) AS p90_cycle_minutes,
    SUM(CASE WHEN idle_minutes < 15 THEN 1 ELSE 0 END) AS gap_count_lt15,
    SUM(CASE WHEN idle_minutes >= 15 AND idle_minutes < 30 THEN 1 ELSE 0 END) AS gap_count_15_29,
    SUM(CASE WHEN idle_minutes >= 30 AND idle_minutes < 60 THEN 1 ELSE 0 END) AS gap_count_30_59,
    SUM(CASE WHEN idle_minutes >= 60 AND idle_minutes < 120 THEN 1 ELSE 0 END) AS gap_count_60_119,
    SUM(CASE WHEN idle_minutes >= 120 THEN 1 ELSE 0 END) AS gap_count_ge120,
    CAST(SUM(CASE WHEN idle_minutes >= 30 THEN idle_minutes ELSE 0 END) AS decimal(12,2)) AS gap_minutes_ge30,
    CAST(MAX(idle_minutes) AS decimal(10,2)) AS max_gap_minutes,
    CAST(DATEDIFF(MINUTE, MIN(session_start), MAX(session_end)) / 60.0 AS decimal(12,2)) AS gross_device_hours,
    CAST((DATEDIFF(MINUTE, MIN(session_start), MAX(session_end)) - SUM(CASE WHEN idle_minutes >= 30 THEN idle_minutes ELSE 0 END)) / 60.0 AS decimal(12,2)) AS net_proxy_hours,
    CAST(600.0 * COUNT_BIG(*) / NULLIF(DATEDIFF(MINUTE, MIN(session_start), MAX(session_end)), 0) AS decimal(12,2)) AS sessions_per_10_gross_hours,
    CAST(600.0 * COUNT_BIG(*) / NULLIF(DATEDIFF(MINUTE, MIN(session_start), MAX(session_end)) - SUM(CASE WHEN idle_minutes >= 30 THEN idle_minutes ELSE 0 END), 0) AS decimal(12,2)) AS sessions_per_10_net_proxy_hours,
    CAST(100.0 * SUM(CASE WHEN fraction_number = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT_BIG(*), 0) AS decimal(10,2)) AS first_fraction_share_pct,
    CAST(100.0 * SUM(CASE WHEN treatment_mode = N'Adaptiv' THEN 1 ELSE 0 END) / NULLIF(COUNT_BIG(*), 0) AS decimal(10,2)) AS adaptive_share_pct
FROM with_percentiles
GROUP BY service_date, machine
ORDER BY service_date, machine;
