{{RESOURCE_BASE}}

;WITH {{SESSION_BASE}},
appointment_deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY DimPatientID, machine, slot_start, slot_end
            ORDER BY appointment_id
        ) AS duplicate_rank
    FROM #appointment_source
    WHERE machine IN (@Machines)
      AND scheduled_minutes IS NOT NULL
),
appointments AS (
    SELECT * FROM appointment_deduplicated WHERE duplicate_rank = 1
),
candidate_matches AS (
    SELECT
        a.*,
        s.DimCourseID,
        s.DimPlanID,
        s.fraction_number,
        s.session_start,
        s.session_end,
        s.actual_minutes,
        ABS(DATEDIFF(MINUTE, a.slot_start, s.session_start)) AS start_delta_minutes,
        ROW_NUMBER() OVER (
            PARTITION BY a.appointment_id
            ORDER BY ABS(DATEDIFF(MINUTE, a.slot_start, s.session_start)), s.session_start
        ) AS appointment_rank,
        ROW_NUMBER() OVER (
            PARTITION BY s.DimPatientID, s.machine, s.session_start
            ORDER BY ABS(DATEDIFF(MINUTE, a.slot_start, s.session_start)), a.slot_start, a.appointment_id
        ) AS session_rank
    FROM appointments a
    INNER JOIN session_metrics s
        ON s.DimPatientID = a.DimPatientID
       AND s.machine = a.machine
       AND s.service_date = a.service_date
       AND s.machine IN (@Machines)
       AND s.session_start BETWEEN DATEADD(HOUR, -2, a.slot_start) AND DATEADD(HOUR, 4, a.slot_start)
),
matched AS (
    SELECT *
    FROM candidate_matches
    WHERE appointment_rank = 1 AND session_rank = 1
),
grouped AS (
    SELECT
        DATEFROMPARTS(YEAR(a.service_date), MONTH(a.service_date), 1) AS period_month,
        a.machine,
        a.activity_code,
        a.activity_name,
        MAX(a.mapping_source) AS mapping_source,
        COUNT_BIG(*) AS relevant_slots,
        COUNT(DISTINCT a.DimPatientID) AS patients,
        COUNT_BIG(m.appointment_id) AS matched_slots,
        AVG(CONVERT(float, a.scheduled_minutes)) AS avg_scheduled_minutes,
        AVG(CONVERT(float, m.actual_minutes)) AS avg_actual_minutes,
        AVG(CASE WHEN a.scheduled_minutes > 0 AND m.actual_minutes IS NOT NULL
                 THEN 100.0 * m.actual_minutes / a.scheduled_minutes END) AS avg_slot_utilization_pct
    FROM appointments a
    LEFT JOIN matched m ON m.appointment_id = a.appointment_id
    GROUP BY DATEFROMPARTS(YEAR(a.service_date), MONTH(a.service_date), 1),
             a.machine, a.activity_code, a.activity_name
    HAVING COUNT(DISTINCT a.DimPatientID) >= @MinimumGroupPatients
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'SlotSummary' AS RecordType,
    period_month,
    machine,
    activity_code,
    activity_name,
    mapping_source,
    relevant_slots,
    patients,
    matched_slots,
    CAST(100.0 * matched_slots / NULLIF(relevant_slots, 0) AS decimal(10,2)) AS match_coverage_pct,
    CAST(avg_scheduled_minutes AS decimal(10,2)) AS avg_scheduled_minutes,
    CAST(avg_actual_minutes AS decimal(10,2)) AS avg_actual_minutes,
    CASE WHEN 100.0 * matched_slots / NULLIF(relevant_slots, 0) >= 50.0
         THEN CAST(avg_slot_utilization_pct AS decimal(10,2)) END AS avg_slot_utilization_pct,
    CASE WHEN 100.0 * matched_slots / NULLIF(relevant_slots, 0) >= 50.0
         THEN N'auswertbar' ELSE N'nicht auswertbar (<50 % Match)' END AS utilization_status
FROM grouped
ORDER BY period_month, machine, relevant_slots DESC;
