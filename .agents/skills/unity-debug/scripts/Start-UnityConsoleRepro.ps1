[CmdletBinding()]
param(
    [string]$ProjectPath,
    [switch]$NoArchive
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$logsDir = Join-Path $resolvedProjectPath "Logs"
$tempDir = Join-Path $resolvedProjectPath "_temp"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

$startedAt = Get-Date
$stamp = $startedAt.ToString("yyyyMMdd_HHmmss")
$encoding = New-Object System.Text.UTF8Encoding($false)
$logFiles = @(
    (Join-Path $logsDir "_compiler_errors.log"),
    (Join-Path $logsDir "_console_errors.log")
)
$archivedLogs = @()

foreach ($logFile in $logFiles) {
    if (-not $NoArchive -and (Test-Path -LiteralPath $logFile) -and (Get-Item -LiteralPath $logFile).Length -gt 0) {
        $archiveName = "UnityConsoleRepro_{0}_{1}" -f $stamp, (Split-Path -Leaf $logFile)
        $archivePath = Join-Path $tempDir $archiveName
        Copy-Item -LiteralPath $logFile -Destination $archivePath -Force
        $archivedLogs += $archivePath
    }

    [System.IO.File]::WriteAllText($logFile, "", $encoding)
}

$markerPath = Join-Path $tempDir "UnityDebug_ReproMarker.json"
$marker = [ordered]@{
    started_at = $startedAt.ToUniversalTime().ToString("o")
    local_started_at = $startedAt.ToString("o")
    project_path = $resolvedProjectPath
    cleared_logs = $logFiles
    archived_logs = $archivedLogs
}
Write-UnityDebugJson -Path $markerPath -Value $marker

Write-Host "[SUCCESS] Unity console repro capture started."
Write-Host "Project: $resolvedProjectPath"
Write-Host ("Started: {0}" -f (Format-UnityDebugTimestamp -Timestamp $startedAt))
Write-Host "Marker: $markerPath"
if ($archivedLogs.Count -gt 0) {
    Write-Host "Archived prior logs:"
    $archivedLogs | ForEach-Object { Write-Host "  $_" }
}
Write-Host ""
Write-Host "Next: reproduce the Unity issue, then run:"
Write-Host ".\.agents\skills\unity-debug\scripts\Invoke-UnityCompile.ps1 -CheckOnly"
