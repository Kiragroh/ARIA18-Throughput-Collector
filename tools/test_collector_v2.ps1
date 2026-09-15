param(
    [Parameter(Mandatory)][string]$ReportServer,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$RdlPath = '',
    [string]$PeriodStart = '2025-01-01',
    [string]$PeriodEnd = '2025-02-28',
    [string]$ContextStart = '2024-01-01',
    [string]$DataThrough = '2025-06-01',
    [string]$PeriodReason = 'Validierung Januar und Februar 2025',
    [string]$SiteLabel = 'Validierung',
    [switch]$IncludeDetails,
    [switch]$TestContext,
    [ValidateSet('EXCELOPENXML','CSV')][string]$Format='EXCELOPENXML'
)
# Execution-session definition only. Does not create or replace catalog reports.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ([string]::IsNullOrWhiteSpace($RdlPath)) {
    $RdlPath=Join-Path $PSScriptRoot '../dist/ARIA18_Throughput_Collector_2.0.rdl'
}
$proxy = New-WebServiceProxy -Uri ($ReportServer.TrimEnd('/')+'/ReportExecution2005.asmx?wsdl') -UseDefaultCredential -Namespace CollectorV2Execution
$proxy.Timeout = 900000
$warnings = $null
$definition=[IO.File]::ReadAllBytes((Get-Item -LiteralPath $RdlPath).FullName)
[xml]$definitionXml=[Text.Encoding]::UTF8.GetString($definition)
$ns=[Xml.XmlNamespaceManager]::new($definitionXml.NameTable)
$ns.AddNamespace('r','http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition')
$sourceHash=(Get-FileHash -LiteralPath $RdlPath -Algorithm SHA256).Hash
if ($TestContext) {
    foreach ($item in @(@('ContextStart',$ContextStart),@('DataThrough',$DataThrough))) {
        $node=$definitionXml.SelectSingleNode("//r:ReportParameter[@Name='"+$item[0]+"']/r:DefaultValue/r:Values/r:Value",$ns)
        $node.InnerText=[datetime]::Parse($item[1]).ToString('yyyy-MM-dd')
    }
    $definition=[Text.Encoding]::UTF8.GetBytes($definitionXml.OuterXml)
    Write-Output 'TEST_CONTEXT_OVERRIDE: temporary definition only; production defaults unchanged'
}
$detailsDefault=$definitionXml.SelectSingleNode("//r:ReportParameter[@Name='IncludePseudonymizedDetails']/r:DefaultValue/r:Values/r:Value",$ns).InnerText -eq 'true'
$effectiveDetails=$IncludeDetails.IsPresent -or $detailsDefault
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$snapshot=Join-Path $OutputDirectory 'tested-definition.rdl'
[IO.File]::WriteAllBytes($snapshot,$definition)
$definitionHash=(Get-FileHash -LiteralPath $snapshot -Algorithm SHA256).Hash
$info = $proxy.LoadReportDefinition($definition,[ref]$warnings)
foreach ($w in $warnings) { Write-Output ('RDL_WARNING: '+$w.Code+' '+$w.Message) }
$parameters = @()
foreach ($item in @(@('PeriodStart',$PeriodStart),@('PeriodEnd',$PeriodEnd),
    @('SiteLabel',$SiteLabel),
    @('ContextStart',$ContextStart),@('DataThrough',$DataThrough),@('PeriodReason',$PeriodReason),
    @('IncludePseudonymizedDetails',$IncludeDetails.IsPresent.ToString().ToLowerInvariant()))) {
    if ($item[0] -eq 'IncludePseudonymizedDetails' -and -not $IncludeDetails.IsPresent) { continue }
    $hidden=$definitionXml.SelectSingleNode("//r:ReportParameter[@Name='"+$item[0]+"']/r:Hidden",$ns)
    if ($hidden -and $hidden.InnerText -eq 'true') { continue }
    $p=New-Object CollectorV2Execution.ParameterValue
    $p.Name=$item[0]; $p.Value=$item[1]; $parameters+=$p
}
$info=$proxy.SetExecutionParameters($parameters,'en-US')
$ContextStart=[datetime]::Parse((@($info.Parameters | Where-Object Name -eq 'ContextStart')[0].DefaultValues[0]),[Globalization.CultureInfo]::InvariantCulture).ToString('yyyy-MM-dd')
$DataThrough=[datetime]::Parse((@($info.Parameters | Where-Object Name -eq 'DataThrough')[0].DefaultValues[0]),[Globalization.CultureInfo]::InvariantCulture).ToString('yyyy-MM-dd')
foreach ($p in $info.Parameters) { if ($p.State -ne 'HasValidValue') { throw ($p.Name+': '+$p.State) } }
$extension=$null; $mime=$null; $encoding=$null; $renderWarnings=$null; $streams=$null
$watch=[Diagnostics.Stopwatch]::StartNew()
$bytes=$proxy.Render($Format,'<DeviceInfo/>',[ref]$extension,[ref]$mime,[ref]$encoding,[ref]$renderWarnings,[ref]$streams)
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$target=Join-Path $OutputDirectory ('collector-v2-'+$PeriodStart+'-'+$PeriodEnd+'.'+$extension)
[IO.File]::WriteAllBytes($target,$bytes)
$watch.Stop()
$release=[regex]::Match($definitionXml.OuterXml,"N'([^']+)' AS collector_release").Groups[1].Value
$evidence=[ordered]@{
    status='rendered'; execution='temporary_definition'; method=$release
    rdl_sha256=$definitionHash; export_sha256=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    source_rdl_sha256=$sourceHash; test_context_override=$TestContext.IsPresent
    period_start=$PeriodStart; period_end=$PeriodEnd; context_start=$ContextStart; data_through=$DataThrough
    format=$Format; details=$effectiveDetails; bytes=$bytes.Length
    seconds=[math]::Round($watch.Elapsed.TotalSeconds,1); recorded_at=[DateTimeOffset]::Now.ToString('o')
}
$evidence | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'execution-evidence.json') -Encoding UTF8
foreach ($w in $renderWarnings) { Write-Output ('RENDER_WARNING: '+$w.Code+' '+$w.Message) }
Write-Output ('RDL_TEMP_EXECUTION_OK bytes='+$bytes.Length+' seconds='+[math]::Round($watch.Elapsed.TotalSeconds,1))
