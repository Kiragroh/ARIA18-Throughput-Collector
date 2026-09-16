SET NOCOUNT ON;
IF @IncludePseudonymizedDetails=0 OR NOT (COL_LENGTH(N'DWH.FactPatientImage',N'DimPatientID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'DimPatientID',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.FactPatientImage',N'DimMachineID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'DimMachineID',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.FactPatientImage',N'ImageCreationDate') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ImageCreationDate',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'DimPatientID',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'IsMOTestPatient',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimMachine',N'OBJECT',N'SELECT',N'DimMachineID',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimMachine',N'OBJECT',N'SELECT',N'MachineId',N'COLUMN'),0)=1)
BEGIN SELECT CAST(NULL AS nvarchar(255)) AS [contract_version],CAST(NULL AS nvarchar(255)) AS [run_id],CAST(NULL AS nvarchar(255)) AS [source],CAST(NULL AS nvarchar(255)) AS [event_key],CAST(NULL AS nvarchar(255)) AS [patient_key],CAST(NULL AS nvarchar(255)) AS [course_key],CAST(NULL AS nvarchar(255)) AS [machine],CAST(NULL AS nvarchar(255)) AS [event_start],CAST(NULL AS nvarchar(255)) AS [event_end],CAST(NULL AS nvarchar(255)) AS [status],CAST(NULL AS nvarchar(255)) AS [activity_code],CAST(NULL AS nvarchar(255)) AS [patient_class],CAST(NULL AS nvarchar(255)) AS [image_kind],CAST(NULL AS nvarchar(255)) AS [image_seconds],CAST(NULL AS nvarchar(255)) AS [image_class_evidence],CAST(NULL AS nvarchar(255)) AS [image_time_source] WHERE 1=0; RETURN; END;
CREATE TABLE #Patient ([DimPatientID] bigint NULL, [IsMOTestPatient] int NULL, [PatientId] nvarchar(255) NULL, [PatientLastName] nvarchar(255) NULL);
IF NOT (COL_LENGTH(N'DWH.DimPatient',N'DimPatientID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'DimPatientID',N'COLUMN'),0)=1) THROW 51001, N'Required source unavailable: DWH.DimPatient.DimPatientID', 1;
IF NOT (COL_LENGTH(N'DWH.DimPatient',N'IsMOTestPatient') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'IsMOTestPatient',N'COLUMN'),0)=1) THROW 51001, N'Required source unavailable: DWH.DimPatient.IsMOTestPatient', 1;
IF OBJECT_ID(N'DWH.DimPatient') IS NOT NULL
BEGIN
DECLARE @sql_Patient nvarchar(max) = N'INSERT INTO #Patient SELECT ' + N'TRY_CONVERT(bigint, s.[DimPatientID])' + N', ' + N'TRY_CONVERT(int, s.[IsMOTestPatient])' + N', ' + CASE WHEN (COL_LENGTH(N'DWH.DimPatient',N'PatientId') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'PatientId',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(nvarchar(255), s.[PatientId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.DimPatient',N'PatientLastName') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimPatient',N'OBJECT',N'SELECT',N'PatientLastName',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(nvarchar(255), s.[PatientLastName])' ELSE N'CAST(NULL AS nvarchar(255))' END + N' FROM DWH.DimPatient s';
EXEC sys.sp_executesql @sql_Patient, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Machine ([DimMachineID] bigint NULL, [MachineId] nvarchar(255) NULL);
IF NOT (COL_LENGTH(N'DWH.DimMachine',N'DimMachineID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimMachine',N'OBJECT',N'SELECT',N'DimMachineID',N'COLUMN'),0)=1) THROW 51001, N'Required source unavailable: DWH.DimMachine.DimMachineID', 1;
IF NOT (COL_LENGTH(N'DWH.DimMachine',N'MachineId') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.DimMachine',N'OBJECT',N'SELECT',N'MachineId',N'COLUMN'),0)=1) THROW 51001, N'Required source unavailable: DWH.DimMachine.MachineId', 1;
IF OBJECT_ID(N'DWH.DimMachine') IS NOT NULL
BEGIN
DECLARE @sql_Machine nvarchar(max) = N'INSERT INTO #Machine SELECT ' + N'TRY_CONVERT(bigint, s.[DimMachineID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[MachineId])' + N' FROM DWH.DimMachine s';
EXEC sys.sp_executesql @sql_Machine, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
CREATE TABLE #Images([DimPatientID] bigint NULL,[DimMachineID] bigint NULL,[ImageCreationDate] datetime2 NULL,[DimCourseID] bigint NULL,[ctrImageSer] bigint NULL,[FactPatientImageID] bigint NULL,[ImageId] nvarchar(255) NULL,[ImageType] nvarchar(255) NULL,[ExposureTime] float NULL);
DECLARE @image_sql nvarchar(max)=N'INSERT INTO #Images SELECT ' + N'TRY_CONVERT(bigint,s.[DimPatientID])' + N', ' + N'TRY_CONVERT(bigint,s.[DimMachineID])' + N', ' + N'TRY_CONVERT(datetime2,s.[ImageCreationDate])' + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'DimCourseID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'DimCourseID',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(bigint,s.[DimCourseID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'ctrImageSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ctrImageSer',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(bigint,s.[ctrImageSer])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'FactPatientImageID') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'FactPatientImageID',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(bigint,s.[FactPatientImageID])' ELSE N'CAST(NULL AS bigint)' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'ImageId') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ImageId',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(nvarchar(255),s.[ImageId])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'ImageType') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ImageType',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(nvarchar(255),s.[ImageType])' ELSE N'CAST(NULL AS nvarchar(255))' END + N', ' + CASE WHEN (COL_LENGTH(N'DWH.FactPatientImage',N'ExposureTime') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'DWH.FactPatientImage',N'OBJECT',N'SELECT',N'ExposureTime',N'COLUMN'),0)=1) THEN N'TRY_CONVERT(float,s.[ExposureTime])' ELSE N'CAST(NULL AS float)' END + N' FROM DWH.FactPatientImage s WHERE s.ImageCreationDate>=@a AND s.ImageCreationDate<DATEADD(day,1,@b)';
EXEC sys.sp_executesql @image_sql,N'@a date,@b date',@a=@PeriodStart,@b=@PeriodEnd;

;WITH source_objects AS (
 SELECT i.*,COALESCE(m.MachineId,N'') AS machine,
 CASE WHEN p.PatientLastName LIKE N'zz%' THEN N'test_name'
      WHEN p.PatientId IS NULL THEN N'unknown'
      WHEN LTRIM(RTRIM(p.PatientId))<>N'' AND p.PatientId NOT LIKE N'%[^0-9]%' THEN N'clinical_numeric'
      ELSE N'clinical_other' END AS patient_class,
 CASE WHEN ctrImageSer IS NOT NULL THEN CONCAT(N'image:',ctrImageSer)
      WHEN FactPatientImageID IS NOT NULL THEN CONCAT(N'fact:',FactPatientImageID)
      ELSE CONCAT(N'natural:',i.DimPatientID,N':',i.DimMachineID,N':',
          CONVERT(nvarchar(33),ImageCreationDate,126),N':',ImageId,N':',ImageType) END AS object_id,
 CASE WHEN UPPER(COALESCE(ImageType,N''))=N'IMAGEDRR' THEN N'reference'
      WHEN UPPER(CONCAT(ImageId,N' ',ImageType)) LIKE N'%EXACTRAC%' THEN N'exactrac_2d'
      WHEN UPPER(CONCAT(ImageId,N' ',ImageType)) LIKE N'%CBCT%' THEN
        CASE WHEN UPPER(ImageId) LIKE N'KV%' THEN N'kv_cbct'
             WHEN UPPER(ImageId) LIKE N'MV%' THEN N'mv_cbct' ELSE N'cbct_unknown' END
      WHEN UPPER(ImageId) LIKE N'KV%' THEN N'kv_2d'
      WHEN UPPER(ImageId) LIKE N'MV%' THEN N'mv_2d'
      WHEN UPPER(ImageType)=N'IMAGEPI' THEN N'unknown_2d' ELSE N'unknown' END AS image_kind
 FROM #Images i JOIN #Patient p ON p.DimPatientID=i.DimPatientID AND p.IsMOTestPatient=0
 LEFT JOIN #Machine m ON m.DimMachineID=i.DimMachineID
 WHERE i.DimPatientID>0
), objects AS (
 SELECT object_id,DimPatientID,
 CASE WHEN COUNT(DISTINCT DimCourseID)=1 THEN MIN(DimCourseID) END AS DimCourseID,
 CASE WHEN COUNT(DISTINCT machine)=1 THEN MIN(machine) ELSE N'AMBIGUOUS_DEVICE' END AS machine,
 MIN(ImageCreationDate) AS created,
 CASE WHEN COUNT(DISTINCT image_kind)=1 THEN MIN(image_kind) ELSE N'unknown' END AS image_kind,
 MAX(CASE WHEN ExposureTime BETWEEN 1 AND 3600000 THEN ExposureTime/1000.0 END) AS seconds,
 MAX(patient_class) AS patient_class
 FROM source_objects GROUP BY object_id,DimPatientID
)
SELECT N'2.0' AS contract_version,@RunId AS run_id,N'image_object' AS source,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':I:',object_id)),2) AS event_key,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':P:',DimPatientID)),2) AS patient_key,
 CASE WHEN DimCourseID IS NOT NULL THEN CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@ExportSalt,N':C:',DimCourseID)),2) END AS course_key,
 machine,created AS event_start,created AS event_end,N'recorded' AS status,N'' AS activity_code,
 patient_class,image_kind,seconds AS image_seconds,N'label_rule_not_acquisition_verified' AS image_class_evidence,
 N'image_creation_not_acquisition' AS image_time_source
FROM objects ORDER BY created,machine;
