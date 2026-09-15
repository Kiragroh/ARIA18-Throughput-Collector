CREATE TABLE #Activity ([DimActivityID] bigint NULL, [ActivityCode] nvarchar(255) NULL, [ActivityNameDEU] nvarchar(1000) NULL, [ActivityCategoryDEU] nvarchar(1000) NULL);
IF COL_LENGTH(N'DWH.DimActivity',N'DimActivityID') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.DimActivityID', 1;
IF COL_LENGTH(N'DWH.DimActivity',N'ActivityCode') IS NULL THROW 51001, N'Required source unavailable: DWH.DimActivity.ActivityCode', 1;
IF OBJECT_ID(N'DWH.DimActivity') IS NOT NULL
BEGIN
DECLARE @sql_Activity nvarchar(max) = N'INSERT INTO #Activity SELECT ' + N'TRY_CONVERT(bigint, s.[DimActivityID])' + N', ' + N'TRY_CONVERT(nvarchar(255), s.[ActivityCode])' + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityNameDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityNameDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N', ' + CASE WHEN COL_LENGTH(N'DWH.DimActivity',N'ActivityCategoryDEU') IS NOT NULL THEN N'TRY_CONVERT(nvarchar(1000), s.[ActivityCategoryDEU])' ELSE N'CAST(NULL AS nvarchar(1000))' END + N' FROM DWH.DimActivity s';
EXEC sys.sp_executesql @sql_Activity, N'@context date,@through date', @context= @ContextStart, @through= @DataThrough;
END;
SELECT DISTINCT ActivityCode AS activity_code,ActivityNameDEU AS activity_name,ActivityCategoryDEU AS activity_category FROM #Activity ORDER BY activity_code;