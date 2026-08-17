WITH {{SESSION_BASE}},
machine_totals AS (
    SELECT
        machine,
        COUNT_BIG(*) AS delivered_sessions,
        COUNT(DISTINCT DimPatientID) AS treated_patients,
        COUNT(DISTINCT service_date) AS active_device_days,
        MIN(service_date) AS first_treatment_date,
        MAX(service_date) AS last_treatment_date
    FROM session_metrics
    WHERE machine <> N'OHNE_GERAET'
    GROUP BY machine
)
SELECT
    machine AS machine_value,
    machine AS machine_label,
    CONCAT(N'M', RIGHT(CONCAT(N'0', DENSE_RANK() OVER (ORDER BY machine)), 2)) AS neutral_machine_index,
    delivered_sessions,
    treated_patients,
    active_device_days,
    first_treatment_date,
    last_treatment_date,
    CASE WHEN delivered_sessions >= 5 AND treated_patients >= 5 THEN 1 ELSE 0 END AS selected_by_default
FROM machine_totals
ORDER BY machine;
