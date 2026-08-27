[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$LaunchRecord,
    [int]$TimeoutSec = 30,
    [switch]$DryRun,
    [switch]$AsJson
)

. "$PSScriptRoot\UnityDebug.Common.ps1"
$ErrorActionPreference = "Stop"

function Write-StopResult {
    param($Result)
    if ($AsJson) { $Result | ConvertTo-Json -Depth 10 } else {
        Write-Host ("Agent-owned Unity stop: {0}" -f $(if ($Result.ok) { $(if ($Result.dryRun) { "dry-run verified" } else { "stopped" }) } else { "blocked" }))
        Write-Host "Launch record: $($Result.launchRecord)"
        if ($Result.pid) { Write-Host "Editor PID: $($Result.pid)" }
        if ($Result.mcpServerPid) { Write-Host "MCP server PID: $($Result.mcpServerPid)" }
        $Result.blockers | ForEach-Object { Write-Host "[BLOCKED] $_" }
    }
}

$recordPath = (Resolve-Path -LiteralPath $LaunchRecord -ErrorAction SilentlyContinue).Path
$recordBlockers = @()
if (-not $recordPath) { $recordBlockers += "Launch record does not exist." }
$record = $null
if ($recordPath) {
    try { $record = Read-UnityDebugJson -Path $recordPath }
    catch { $recordBlockers += "Launch record is not valid JSON." }
}
$recordIsObject = $record -is [pscustomobject] -or $record -is [System.Collections.IDictionary]
if ($recordPath -and -not $recordIsObject) {
    $recordBlockers += "Launch record must contain one JSON object."
    $record = $null
}
$recordPid = 0
$recordSchemaVersion = 0
if ($record) {
    if (-not [int]::TryParse([string]$record.pid, [ref]$recordPid) -or $recordPid -le 0) {
        $recordBlockers += "Launch record has an invalid Editor PID."
    }
    if ([string]::IsNullOrWhiteSpace([string]$record.projectPath)) {
        $recordBlockers += "Launch record has no project path."
    }
    else {
        try {
            $expectedDirectory = Join-Path ([string]$record.projectPath) "_temp"
            $expectedPrefix = [System.IO.Path]::GetFullPath($expectedDirectory) + [System.IO.Path]::DirectorySeparatorChar
            $comparison = if ($IsWindows) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
            if (-not $recordPath.StartsWith($expectedPrefix, $comparison)) {
                $recordBlockers += "Launch record is not inside the recorded project's ignored _temp directory."
            }
        }
        catch {
            $recordBlockers += "Launch record has an invalid project path."
        }
    }
    if (-not [int]::TryParse([string]$record.schemaVersion, [ref]$recordSchemaVersion) -or
        [string]$record.owner -ne "agent" -or $recordSchemaVersion -ne 1) {
        $recordBlockers += "Launch record does not identify an agent-owned Editor."
    }
}

$blockers = @($recordBlockers)
$safeProcess = $null
$editorAlreadyStopped = $false
if ($record -and $recordBlockers.Count -eq 0) {
    $candidate = Get-Process -Id $recordPid -ErrorAction SilentlyContinue
    $unityState = @(Get-UnityEditorProcesses | Where-Object { $_.Id -eq $recordPid }) | Select-Object -First 1
    if (-not $candidate -and -not $unityState) {
        $editorAlreadyStopped = $true
    }
    elseif (-not $candidate -or -not $unityState) {
        $blockers += "The recorded PID exists in an ambiguous or non-Unity state."
    }
    elseif (-not (Test-UnityPathEqual $unityState.ProjectPath ([string]$record.projectPath))) {
        $blockers += "The PID does not own the recorded project."
    }
    elseif ($unityState.ExecutablePath -and -not (Test-UnityPathEqual $unityState.ExecutablePath ([string]$record.unityPath))) {
        $blockers += "The PID executable does not match the launch record."
    }
    else {
        $recordedStart = ConvertTo-UnityDebugUtcDateTime -Value $record.processStartTimeUtc
        if (-not $recordedStart) {
            $blockers += "Launch record has an invalid Editor process start time."
        }
        elseif ([math]::Abs(($candidate.StartTime.ToUniversalTime() - $recordedStart).TotalSeconds) -gt 2) {
            $blockers += "The PID start time does not match the launch record."
        }
        else { $safeProcess = $candidate }
    }
}

$mcpServerRecord = if ($record -and $record.PSObject.Properties["mcpServer"]) { $record.mcpServer } else { $null }
$mcpServerPid = 0
if ($mcpServerRecord) { [void][int]::TryParse([string]$mcpServerRecord.pid, [ref]$mcpServerPid) }
$result = [pscustomobject]@{
    ok = $false
    dryRun = [bool]$DryRun
    launchRecord = $recordPath
    pid = if ($recordPid -gt 0) { $recordPid } else { $null }
    editorAlreadyStopped = $editorAlreadyStopped
    editorStopped = $false
    mcpServerPid = if ($mcpServerPid -gt 0) { $mcpServerPid } else { $null }
    mcpServerStopped = $null
    blockers = @($blockers)
}
if ($recordBlockers.Count -gt 0) { Write-StopResult $result; exit 1 }

if ($DryRun) {
    if ($mcpServerRecord) {
        $mcpDryRun = Stop-UnityMcpServerFromOwnershipRecord -Record $mcpServerRecord -TimeoutSec 15 -DryRun
        if (-not $mcpDryRun.ok) {
            $blockers += @($mcpDryRun.blockers)
        }
        else { $result.mcpServerStopped = [bool]$mcpDryRun.alreadyStopped }
    }
    $result.blockers = @($blockers)
    $result.ok = $blockers.Count -eq 0
    Write-StopResult $result
    if ($result.ok) { exit 0 } else { exit 1 }
}

if ($safeProcess) {
    # Stop-Process without -Force requests normal termination on macOS and Windows. Never escalate automatically.
    Stop-Process -Id $safeProcess.Id -ErrorAction Stop
    try {
        Wait-Process -Id $safeProcess.Id -Timeout $TimeoutSec -ErrorAction Stop
    }
    catch {
        $result.blockers = @("Unity did not exit within $TimeoutSec seconds; no forced termination was attempted.")
        Write-StopResult $result
        exit 1
    }
    $result.editorStopped = $true
}

if ($mcpServerRecord) {
    $mcpStop = Stop-UnityMcpServerFromOwnershipRecord -Record $mcpServerRecord -TimeoutSec 15
    if (-not $mcpStop.ok) {
        $blockers += @($mcpStop.blockers)
    }
    else { $result.mcpServerStopped = $true }
}

$stoppedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
if ($blockers.Count -eq 0) {
    $record | Add-Member -NotePropertyName stoppedAtUtc -NotePropertyValue $stoppedAtUtc -Force
}
if ($result.editorStopped -or $editorAlreadyStopped) {
    $record | Add-Member -NotePropertyName editorStoppedAtUtc -NotePropertyValue $stoppedAtUtc -Force
}
if ($mcpServerRecord -and $result.mcpServerStopped) {
    $record | Add-Member -NotePropertyName mcpServerStoppedAtUtc -NotePropertyValue $stoppedAtUtc -Force
}
Write-UnityDebugJson -Path $recordPath -Value $record
$result.blockers = @($blockers)
$result.ok = $blockers.Count -eq 0
Write-StopResult $result
if (-not $result.ok) { exit 1 }
