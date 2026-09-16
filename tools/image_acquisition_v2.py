"""Optional native image enrichment, joined by salted image identity, not patient/day."""
FIELDS = ['contract_version','run_id','source_state','event_key','event_start',
          'acquisition_kind','image_manufacturer','acquisition_machine','acquisition_time']
REQUIRED = {
    'Image': ['ImageSer','CreationDate','ImageType'],
    'ImageSlice': ['ImageSer','SliceSer'],
    'Slice': ['SliceSer','SliceModality','EquipmentSer','ResourceSer','AcquisitionDateTime'],
    'Equipment': ['EquipmentSer','Manufacturer','ModelName'],
    'Machine': ['ResourceSer','MachineId'],
    'SliceRT': ['SliceSer','ReferenceImage','PrimaryDosimeterUnit'],
}


def query():
    try:
        from .build_collector_v2 import column_available, lit
    except ImportError:
        from build_collector_v2 import column_available, lit
    missing = ' OR '.join('NOT '+column_available('dbo.'+table,column)
                         for table,columns in REQUIRED.items() for column in columns)
    empty = ','.join("N'2.0' AS contract_version" if f=='contract_version' else
                    '@RunId AS run_id' if f=='run_id' else "N'UNAVAILABLE' AS source_state" if f=='source_state'
                    else f'CAST(NULL AS nvarchar(255)) AS {f}' for f in FIELDS)
    sql = """
;WITH evidence AS (
 SELECT i.ImageSer,i.CreationDate,s.AcquisitionDateTime,m.MachineId,
 CASE WHEN UPPER(e.Manufacturer) LIKE N'%BRAINLAB%' THEN N'Brainlab'
      WHEN UPPER(e.Manufacturer) LIKE N'%VARIAN%' THEN N'Varian' ELSE N'Other / unknown' END AS vendor,
 CASE WHEN i.ImageType=N'ImageDRR' OR rt.ReferenceImage=1 THEN N'reference'
      WHEN i.ImageType=N'ImagePI' AND s.SliceModality=N'RTIMAGE' THEN
        CASE WHEN UPPER(e.Manufacturer) LIKE N'%BRAINLAB%' THEN N'exactrac_2d'
             WHEN rt.PrimaryDosimeterUnit=N'MINUTE' THEN N'kv_2d'
             WHEN rt.PrimaryDosimeterUnit=N'MU' THEN N'mv_2d' ELSE N'unknown_2d' END
      WHEN i.ImageType=N'Image' AND s.SliceModality=N'CT'
       AND UPPER(e.Manufacturer) LIKE N'%VARIAN%'
       AND (UPPER(e.ModelName) LIKE N'%PATIENT VERIFICATION%' OR UPPER(e.ModelName) LIKE N'%HALCYON%PVA%')
        THEN N'cbct_unknown' ELSE N'unknown' END AS kind
 FROM dbo.Image i JOIN dbo.ImageSlice ix ON ix.ImageSer=i.ImageSer
 JOIN dbo.Slice s ON s.SliceSer=ix.SliceSer
 LEFT JOIN dbo.Equipment e ON e.EquipmentSer=s.EquipmentSer
 LEFT JOIN dbo.Machine m ON m.ResourceSer=s.ResourceSer
 LEFT JOIN dbo.SliceRT rt ON rt.SliceSer=s.SliceSer
 WHERE i.CreationDate>=@a AND i.CreationDate<DATEADD(day,1,@b)
 AND i.ImageType IN (N'Image',N'ImagePI',N'ImageDRR')
)
SELECT N'2.0' AS contract_version,@run AS run_id,N'AVAILABLE' AS source_state,
 CONVERT(varchar(64),HASHBYTES('SHA2_256',CONCAT(@salt,N':I:image:',ImageSer)),2) AS event_key,
 MIN(CreationDate) AS event_start,
 CASE WHEN COUNT(DISTINCT kind)=1 THEN MIN(kind) ELSE N'unknown' END AS acquisition_kind,
 CASE WHEN COUNT(DISTINCT vendor)=1 THEN MIN(vendor) ELSE N'Other / unknown' END AS image_manufacturer,
 CASE WHEN COUNT(DISTINCT MachineId)=1 THEN MIN(MachineId) END AS acquisition_machine,
 MIN(AcquisitionDateTime) AS acquisition_time
FROM evidence GROUP BY ImageSer;
"""
    return ('SET NOCOUNT ON; IF @IncludePseudonymizedDetails=0 OR '+missing+
            ' BEGIN SELECT '+empty+'; RETURN; END;\nDECLARE @sql nvarchar(max)='+lit(sql)+
            "; EXEC sys.sp_executesql @sql,N'@a date,@b date,@run nvarchar(255),@salt nvarchar(255)',"
            '@a=@PeriodStart,@b=@PeriodEnd,@run=@RunId,@salt=@ExportSalt;')
