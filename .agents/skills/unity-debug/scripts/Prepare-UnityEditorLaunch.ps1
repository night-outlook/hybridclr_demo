[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string]$UnityPath,
    [int]$TimeoutSec = 600,
    [switch]$DryRun,
    [switch]$AsJson
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

$ErrorActionPreference = "Stop"
$autoConnectMarker = "[MCP-CI] AUTOCONNECT_READY project-scoped=true transport=http scope=local"

function Write-PreparationResult {
    param([Parameter(Mandatory = $true)]$Result)

    if ($AsJson) {
        $Result | ConvertTo-Json -Depth 8
    }
    else {
        Write-Host ("Preparation: {0}" -f $(if ($Result.ok) { "ready" } else { "blocked" }))
        Write-Host "Project: $($Result.projectPath)"
        Write-Host "Log: $($Result.logFile)"
        if ($Result.blockers.Count -gt 0) { $Result.blockers | ForEach-Object { Write-Host "[BLOCKED] $_" } }
    }
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
if (Test-UnityProjectRunning -ProjectPath $resolvedProjectPath) {
    Write-PreparationResult ([pscustomobject]@{ ok = $false; dryRun = [bool]$DryRun; projectPath = $resolvedProjectPath; logFile = $null; blockers = @("The exact project is already open. Batchmode must not run against an open project.") })
    exit 1
}

if ([string]::IsNullOrWhiteSpace($UnityPath)) { $UnityPath = Get-ConfiguredUnityPath }
$resolvedUnityPath = if ($UnityPath) { Resolve-UnityExecutablePath -Path $UnityPath } else { $null }
if (-not $resolvedUnityPath) {
    Write-PreparationResult ([pscustomobject]@{ ok = $false; dryRun = [bool]$DryRun; projectPath = $resolvedProjectPath; logFile = $null; blockers = @("Unity executable is not configured or does not exist.") })
    exit 1
}

$tempDir = Join-Path $resolvedProjectPath "_temp"
if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $tempDir | Out-Null }
$logFile = Join-Path $tempDir ("UnityEditorPrepare_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss_fff"))
$arguments = @(
    "-batchmode", "-quit",
    "-projectPath", $resolvedProjectPath,
    "-executeMethod", "MCPForUnity.Editor.McpCiBoot.EnableHttpAutoConnectForCurrentProject",
    "-logFile", $logFile
)

if ($DryRun) {
    $result = [pscustomobject]@{
        ok = $true
        dryRun = $true
        projectPath = $resolvedProjectPath
        unityPath = $resolvedUnityPath
        arguments = @($arguments)
        logFile = $logFile
        blockers = @()
    }
    Write-PreparationResult $result
    if (-not $AsJson) { Write-Host "[DRY RUN] $resolvedUnityPath $(Format-NativeArgumentList -ArgumentList $arguments)" }
    exit 0
}

$before = Get-UnityLaunchSourceSnapshot -Root $resolvedProjectPath
$startedAt = (Get-Date).ToUniversalTime()
$blockers = @()
$exitCode = $null
$timedOut = $false

try {
    # This is intentionally the sole batchmode invocation in the visible-Editor preparation.
    $process = Start-UnityNativeProcess -FilePath $resolvedUnityPath -ArgumentList $arguments -WorkingDirectory $resolvedProjectPath -Hidden
    if (-not $process.WaitForExit($TimeoutSec * 1000)) {
        $timedOut = $true
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $blockers += "Unity preparation timed out after $TimeoutSec seconds; the timed-out batch process was terminated."
    }
    else {
        $exitCode = $process.ExitCode
        if ($exitCode -ne 0) { $blockers += "Unity preparation exited with code $exitCode." }
    }
}
catch {
    $blockers += "Unity preparation could not run: $($_.Exception.Message)"
}

$logText = ""
if (-not (Test-Path -LiteralPath $logFile -PathType Leaf)) {
    $blockers += "The dedicated preparation log is missing."
}
else {
    $logItem = Get-Item -LiteralPath $logFile
    if ($logItem.LastWriteTimeUtc -lt $startedAt.AddSeconds(-2)) { $blockers += "The preparation log is stale." }
    $logText = Get-Content -Raw -Encoding UTF8 -LiteralPath $logFile
    if ($logText -match '(?im)\berror CS\d+:|Compilation failed|Compiler errors|Scripts have compiler errors') {
        $blockers += "Compiler diagnostics were found in the preparation log."
    }
    if (-not $logText.Contains($autoConnectMarker)) { $blockers += "The MCP AutoConnect success marker is missing." }
}

$after = Get-UnityLaunchSourceSnapshot -Root $resolvedProjectPath
if ($before.Path -ne $after.Path -or $before.LastWriteTimeUtc -ne $after.LastWriteTimeUtc) {
    $blockers += "Relevant project source changed after validation started. Run preparation again against the new source state."
}

$result = [pscustomobject]@{
    ok = $blockers.Count -eq 0
    dryRun = $false
    projectPath = $resolvedProjectPath
    unityPath = $resolvedUnityPath
    exitCode = $exitCode
    timedOut = $timedOut
    autoConnectMarkerFound = $logText.Contains($autoConnectMarker)
    logFile = $logFile
    startedAtUtc = $startedAt.ToString("o")
    sourceBefore = $before
    sourceAfter = $after
    blockers = @($blockers)
}
Write-PreparationResult $result
exit $(if ($result.ok) { 0 } else { 1 })
