{{RESOURCE_BASE}}

;WITH {{SESSION_BASE}},
appointment_deduplicated AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY DimPatientID, machine, slot_start, slot_end ORDER BY appointment_id
    ) AS duplicate_rank
    FROM #appointment_source
    WHERE machine IN (@Machines)
),
candidate_matches AS (
    SELECT a.*,
           s.session_start, s.session_end, s.actual_minutes,
           s.first_imaging_timestamp, s.first_beam_timestamp, s.clinical_start_timestamp,
           s.clinical_span_minutes, s.imaging_after_beam_flag,
           ROW_NUMBER() OVER (PARTITION BY a.appointment_id
                              ORDER BY ABS(DATEDIFF(MINUTE, a.slot_start, s.session_start)), s.session_start) AS appointment_rank,
           ROW_NUMBER() OVER (PARTITION BY s.DimPatientID, s.machine, s.session_start
                              ORDER BY ABS(DATEDIFF(MINUTE, a.slot_start, s.session_start)), a.appointment_id) AS session_rank
    FROM appointment_deduplicated a
    LEFT JOIN session_metrics s
      ON s.DimPatientID = a.DimPatientID AND s.machine = a.machine AND s.service_date = a.service_date
     AND s.session_start BETWEEN DATEADD(HOUR, -2, a.slot_start) AND DATEADD(HOUR, 4, a.slot_start)
    WHERE a.duplicate_rank = 1
),
final_rows AS (
    SELECT * FROM candidate_matches
    WHERE session_start IS NULL OR (appointment_rank = 1 AND session_rank = 1)
)
SELECT
    @MethodVersion AS MethodVersion,
    @RunId AS RunId,
    @SiteLabel AS SiteLabel,
    N'AppointmentDetails' AS RecordType,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':PAT:', DimPatientID)), 2) AS patient_key,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':APPOINTMENT:', appointment_id)), 2) AS appointment_key,
    CASE WHEN session_start IS NOT NULL THEN
        CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(@ExportSalt, N':SESSION:', DimPatientID, N':', machine, N':', CONVERT(varchar(33), session_start, 126))), 2)
    END AS matched_session_key,
    service_date,
    machine,
    slot_start,
    slot_end,
    scheduled_minutes,
    activity_start,
    activity_end,
    activity_minutes,
    activity_code,
    activity_name,
    activity_category,
    mapping_source,
    patient_arrival_timestamp,
    arrival_source,
    appointment_status,
    checked_in,
    pending_or_in_progress_timestamp,
    pending_or_in_progress_status,
    completed_timestamp,
    completed_status,
    first_imaging_timestamp AS matched_first_imaging_timestamp,
    first_beam_timestamp AS matched_first_beam_timestamp,
    clinical_start_timestamp AS matched_clinical_start_timestamp,
    session_start AS matched_session_start,
    session_end AS matched_session_end,
    CAST(actual_minutes AS decimal(10,2)) AS matched_actual_minutes,
    CAST(clinical_span_minutes AS decimal(10,2)) AS matched_clinical_span_minutes,
    imaging_after_beam_flag,
    CASE
        WHEN patient_arrival_timestamp IS NULL THEN N'missing'
        WHEN clinical_start_timestamp IS NULL THEN N'no_matched_clinical_start'
        WHEN patient_arrival_timestamp > clinical_start_timestamp THEN N'after_clinical_start'
        WHEN DATEDIFF(MINUTE, patient_arrival_timestamp, clinical_start_timestamp) > 360 THEN N'earlier_than_6h'
        ELSE N'usable'
    END AS arrival_timing_quality,
    CAST(CASE WHEN patient_arrival_timestamp IS NOT NULL AND clinical_start_timestamp IS NOT NULL
              AND DATEDIFF(MINUTE, patient_arrival_timestamp, clinical_start_timestamp) BETWEEN 0 AND 360
              THEN DATEDIFF(SECOND, patient_arrival_timestamp, clinical_start_timestamp) / 60.0 END AS decimal(10,2))
        AS arrival_to_clinical_start_minutes,
    CAST(CASE WHEN slot_start IS NOT NULL AND clinical_start_timestamp IS NOT NULL
              AND DATEDIFF(MINUTE, slot_start, clinical_start_timestamp) BETWEEN -120 AND 240
              THEN DATEDIFF(SECOND, slot_start, clinical_start_timestamp) / 60.0 END AS decimal(10,2))
        AS slot_to_clinical_start_minutes,
    CAST(CASE WHEN pending_or_in_progress_timestamp IS NOT NULL AND clinical_start_timestamp IS NOT NULL
              AND DATEDIFF(MINUTE, pending_or_in_progress_timestamp, clinical_start_timestamp) BETWEEN 0 AND 240
              THEN DATEDIFF(SECOND, pending_or_in_progress_timestamp, clinical_start_timestamp) / 60.0 END AS decimal(10,2))
        AS pending_to_clinical_start_minutes,
    CAST(CASE WHEN patient_arrival_timestamp IS NOT NULL AND pending_or_in_progress_timestamp IS NOT NULL
              AND DATEDIFF(MINUTE, patient_arrival_timestamp, pending_or_in_progress_timestamp) BETWEEN 0 AND 360
              THEN DATEDIFF(SECOND, patient_arrival_timestamp, pending_or_in_progress_timestamp) / 60.0 END AS decimal(10,2))
        AS arrival_to_pending_minutes,
    CAST(CASE WHEN clinical_start_timestamp IS NOT NULL AND completed_timestamp IS NOT NULL
              AND DATEDIFF(MINUTE, clinical_start_timestamp, completed_timestamp) BETWEEN 0 AND 240
              THEN DATEDIFF(SECOND, clinical_start_timestamp, completed_timestamp) / 60.0 END AS decimal(10,2))
        AS clinical_start_to_completed_minutes
FROM final_rows
WHERE @IncludePseudonymizedDetails = 1
ORDER BY service_date, machine, slot_start;
