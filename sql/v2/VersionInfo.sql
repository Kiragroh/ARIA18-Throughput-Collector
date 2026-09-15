SET NOCOUNT ON;
SELECT N'TESTED' AS source_state,N'ARIA-DWH' AS component,N'18' AS version_or_source,
 N'Bisher gegen ARIA 18 geprueft; keine automatische Versionsgarantie' AS interpretation
UNION ALL SELECT N'AVAILABLE',N'SQL Server',CONVERT(nvarchar(255),SERVERPROPERTY('ProductVersion')),
 N'SQL-Version, nicht ARIA-Version'
UNION ALL SELECT N'NOT_DETECTED',N'Installierte ARIA-Version',N'',
 N'Bei Abweichung oder Rueckfragen optional im Standortformular angeben'
UNION ALL SELECT N'SCHEMA_CANDIDATE',N'Versionsmetadaten',s.name+N'.'+t.name+N'.'+c.name,
 N'Nur Spaltennachweis; kein als ARIA-Version interpretierter Wert'
FROM sys.objects t JOIN sys.schemas s ON s.schema_id=t.schema_id JOIN sys.columns c ON c.object_id=t.object_id
WHERE t.type IN ('U','V') AND s.name=N'DWH' AND (c.name LIKE N'%Version%' OR t.name LIKE N'%Version%');
