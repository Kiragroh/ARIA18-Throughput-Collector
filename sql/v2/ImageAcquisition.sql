SET NOCOUNT ON; IF @IncludePseudonymizedDetails=0 OR NOT (COL_LENGTH(N'dbo.Image',N'ImageSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Image',N'OBJECT',N'SELECT',N'ImageSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Image',N'CreationDate') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Image',N'OBJECT',N'SELECT',N'CreationDate',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Image',N'ImageType') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Image',N'OBJECT',N'SELECT',N'ImageType',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.ImageSlice',N'ImageSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ImageSlice',N'OBJECT',N'SELECT',N'ImageSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.ImageSlice',N'SliceSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.ImageSlice',N'OBJECT',N'SELECT',N'SliceSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Slice',N'SliceSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Slice',N'OBJECT',N'SELECT',N'SliceSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Slice',N'SliceModality') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Slice',N'OBJECT',N'SELECT',N'SliceModality',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Slice',N'EquipmentSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Slice',N'OBJECT',N'SELECT',N'EquipmentSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Slice',N'ResourceSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Slice',N'OBJECT',N'SELECT',N'ResourceSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Slice',N'AcquisitionDateTime') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Slice',N'OBJECT',N'SELECT',N'AcquisitionDateTime',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Equipment',N'EquipmentSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Equipment',N'OBJECT',N'SELECT',N'EquipmentSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Equipment',N'Manufacturer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Equipment',N'OBJECT',N'SELECT',N'Manufacturer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Equipment',N'ModelName') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Equipment',N'OBJECT',N'SELECT',N'ModelName',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Machine',N'ResourceSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Machine',N'OBJECT',N'SELECT',N'ResourceSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.Machine',N'MachineId') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.Machine',N'OBJECT',N'SELECT',N'MachineId',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.SliceRT',N'SliceSer') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.SliceRT',N'OBJECT',N'SELECT',N'SliceSer',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.SliceRT',N'ReferenceImage') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.SliceRT',N'OBJECT',N'SELECT',N'ReferenceImage',N'COLUMN'),0)=1) OR NOT (COL_LENGTH(N'dbo.SliceRT',N'PrimaryDosimeterUnit') IS NOT NULL AND COALESCE(HAS_PERMS_BY_NAME(N'dbo.SliceRT',N'OBJECT',N'SELECT',N'PrimaryDosimeterUnit',N'COLUMN'),0)=1) BEGIN SELECT N'2.0' AS contract_version,@RunId AS run_id,N'UNAVAILABLE' AS source_state,CAST(NULL AS nvarchar(255)) AS event_key,CAST(NULL AS nvarchar(255)) AS event_start,CAST(NULL AS nvarchar(255)) AS acquisition_kind,CAST(NULL AS nvarchar(255)) AS image_manufacturer,CAST(NULL AS nvarchar(255)) AS acquisition_machine,CAST(NULL AS nvarchar(255)) AS acquisition_time; RETURN; END;
DECLARE @sql nvarchar(max)=N'
;WITH evidence AS (
 SELECT i.ImageSer,i.CreationDate,s.AcquisitionDateTime,m.MachineId,
 CASE WHEN UPPER(e.Manufacturer) LIKE N''%BRAINLAB%'' THEN N''Brainlab''
      WHEN UPPER(e.Manufacturer) LIKE N''%VARIAN%'' THEN N''Varian'' ELSE N''Other / unknown'' END AS vendor,
 CASE WHEN i.ImageType=N''ImageDRR'' OR rt.ReferenceImage=1 THEN N''reference''
      WHEN i.ImageType=N''ImagePI'' AND s.SliceModality=N''RTIMAGE'' THEN
        CASE WHEN UPPER(e.Manufacturer) LIKE N''%BRAINLAB%'' THEN N''exactrac_2d''
             WHEN rt.PrimaryDosimeterUnit=N''MINUTE'' THEN N''kv_2d''
             WHEN rt.PrimaryDosimeterUnit=N''MU'' THEN N''mv_2d'' ELSE N''unknown_2d'' END
      WHEN i.ImageType=N''Image'' AND s.SliceModality=N''CT''
       AND UPPER(e.Manufacturer) LIKE N''%VARIAN%''
       AND (UPPER(e.ModelName) LIKE N''%PATIENT VERIFICATION%'' OR UPPER(e.ModelName) LIKE N''%HALCYON%PVA%'')
        THEN N''cbct_unknown'' ELSE N''unknown'' END AS kind
 FROM dbo.Image i JOIN dbo.ImageSlice ix ON ix.ImageSer=i.ImageSer
 JOIN dbo.Slice s ON s.SliceSer=ix.SliceSer
 LEFT JOIN dbo.Equipment e ON e.EquipmentSer=s.EquipmentSer
 LEFT JOIN dbo.Machine m ON m.ResourceSer=s.ResourceSer
 LEFT JOIN dbo.SliceRT rt ON rt.SliceSer=s.SliceSer
 WHERE i.CreationDate>=@a AND i.CreationDate<DATEADD(day,1,@b)
 AND i.ImageType IN (N''Image'',N''ImagePI'',N''ImageDRR'')
)
SELECT N''2.0'' AS contract_version,@run AS run_id,N''AVAILABLE'' AS source_state,
 CONVERT(varchar(64),HASHBYTES(''SHA2_256'',CONCAT(@salt,N'':I:image:'',ImageSer)),2) AS event_key,
 MIN(CreationDate) AS event_start,
 CASE WHEN COUNT(DISTINCT kind)=1 THEN MIN(kind) ELSE N''unknown'' END AS acquisition_kind,
 CASE WHEN COUNT(DISTINCT vendor)=1 THEN MIN(vendor) ELSE N''Other / unknown'' END AS image_manufacturer,
 CASE WHEN COUNT(DISTINCT MachineId)=1 THEN MIN(MachineId) END AS acquisition_machine,
 MIN(AcquisitionDateTime) AS acquisition_time
FROM evidence GROUP BY ImageSer;
'; EXEC sys.sp_executesql @sql,N'@a date,@b date,@run nvarchar(255),@salt nvarchar(255)',@a=@PeriodStart,@b=@PeriodEnd,@run=@RunId,@salt=@ExportSalt;