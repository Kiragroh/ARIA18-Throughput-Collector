[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ReportServer,
    [string]$RdlPath = '',
    [string]$OutputDirectory = '',
    [string]$ParentPath = '/',
    [datetime]$PeriodStart = (Get-Date -Day 1).AddMonths(-1),
    [datetime]$PeriodEnd = (Get-Date -Day 1).AddDays(-1),
    [string[]]$Machines = @(),
    [ValidateSet('PDF', 'EXCELOPENXML')]
    [string[]]$Formats = @('PDF', 'EXCELOPENXML'),
    [switch]$IncludeDetails,
    [switch]$DiscoverOnly,
    [switch]$KeepTestReport
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RdlPath)) {
    $RdlPath = Join-Path $scriptDirectory '..\dist\ARIA18_Durchsatz_Klinikvergleich_Collector.rdl'
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $scriptDirectory '..\validation\ssrs_http'
}

if (-not (Test-Path -LiteralPath $RdlPath -PathType Leaf)) {
    throw "RDL nicht gefunden: $RdlPath"
}

$resolvedRdl = (Get-Item -LiteralPath $RdlPath).FullName
$serviceUri = $ReportServer.TrimEnd('/') + '/ReportService2010.asmx?wsdl'
$reportName = 'ARIA18_Durchsatz_Klinikvergleich_Collector_TEST_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$normalizedParent = if ($ParentPath -eq '/') { '' } else { $ParentPath.TrimEnd('/') }
$reportPath = $normalizedParent + '/' + $reportName
$published = $false
$warnings = $null

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

try {
    $proxy = New-WebServiceProxy -Uri $serviceUri -UseDefaultCredential -Namespace 'SSRS2010'
    if ($DiscoverOnly) {
        foreach ($catalogItem in @($proxy.ListChildren('/', $false))) {
            Write-Output "SSRS_ITEM: $($catalogItem.TypeName) | $($catalogItem.Path)"
        }
        return
    }
    $bytes = [IO.File]::ReadAllBytes($resolvedRdl)
    $item = $proxy.CreateCatalogItem('Report', $reportName, $ParentPath, $false, $bytes, $null, [ref]$warnings)
    $published = $true
    Write-Output "SSRS_PUBLISHED: $($item.Path)"

    if ($warnings) {
        foreach ($warning in @($warnings)) {
            Write-Output "SSRS_WARNING: $($warning.Code) | $($warning.Message)"
        }
    }
    else {
        Write-Output 'SSRS_WARNINGS: NONE'
    }

    $query = [System.Collections.Generic.List[string]]::new()
    $query.Add('rs:Command=Render')
    $query.Add('SiteLabel=' + [uri]::EscapeDataString('SSRS HTTP Test'))
    $query.Add('PeriodStart=' + $PeriodStart.ToString('yyyy-MM-dd'))
    $query.Add('PeriodEnd=' + $PeriodEnd.ToString('yyyy-MM-dd'))
    foreach ($machine in $Machines) {
        $query.Add('Machines=' + [uri]::EscapeDataString($machine))
    }
    $query.Add('MinimumGroupPatients=5')
    $query.Add('IncludePseudonymizedDetails=' + $IncludeDetails.IsPresent.ToString().ToLowerInvariant())

    foreach ($format in $Formats) {
        $extension = if ($format -eq 'PDF') { '.pdf' } else { '.xlsx' }
        $target = Join-Path $OutputDirectory ($reportName + $extension)
        $renderUrl = $ReportServer.TrimEnd('/') + '?' + $reportPath + '&' + ($query -join '&') + '&rs:Format=' + $format
        Invoke-WebRequest -Uri $renderUrl -UseDefaultCredentials -UseBasicParsing -TimeoutSec 900 -OutFile $target
        $file = Get-Item -LiteralPath $target
        if ($file.Length -lt 1024) {
            throw "SSRS-Export ist unerwartet klein: $target ($($file.Length) Bytes)"
        }
        Write-Output "SSRS_RENDER_OK: $format | $($file.Length) Bytes | $target"
    }
}
finally {
    if ($published -and -not $KeepTestReport) {
        try {
            $proxy.DeleteItem($reportPath)
            Write-Output "SSRS_TEST_REPORT_REMOVED: $reportPath"
        }
        catch {
            Write-Warning "Testbericht konnte nicht entfernt werden: $reportPath | $($_.Exception.Message)"
        }
    }
}
