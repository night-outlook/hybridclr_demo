[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string]$UnityPath,
    [string]$ScenePath = "Assets/Scenes/SampleScene.unity",
    [double]$MinimumAvailableMemoryGB = 4,
    [switch]$ForceLowMemory,
    [int]$PreparationTimeoutSec = 600,
    [int]$StartupTimeoutSec = 120,
    [int]$StartupStabilitySec = 10,
    [switch]$DryRun,
    [switch]$AsJson
)

. "$PSScriptRoot\UnityDebug.Common.ps1"
$ErrorActionPreference = "Stop"

function Write-LaunchResult {
    param([Parameter(Mandatory = $true)]$Result)
    if ($AsJson) { $Result | ConvertTo-Json -Depth 10; return }
    Write-Host ("Visible Editor launch: {0}" -f $(if ($Result.ok) { $(if ($Result.dryRun) { "dry-run ready" } else { "started" }) } else { "blocked" }))
    Write-Host "Project: $($Result.projectPath)"
    if ($Result.memory) { Write-Host ("Available memory: {0} GB ({1}); other Unity Editors: {2}" -f $Result.memory.AvailableGB, $Result.memory.Source, $Result.otherEditorCount) }
    if ($Result.pid) { Write-Host "PID: $($Result.pid)" }
    if ($Result.launchLog) { Write-Host "Launch log: $($Result.launchLog)" }
    if ($Result.launchRecord) { Write-Host "Launch record: $($Result.launchRecord)" }
    $Result.blockers | ForEach-Object { Write-Host "[BLOCKED] $_" }
}

function New-LaunchResult {
    param([string]$Project, $Memory, [int]$OtherCount, [string[]]$Blockers)
    return [pscustomobject]@{
        ok = $false; dryRun = [bool]$DryRun; projectPath = $Project; permission = $null
        memory = $Memory; otherEditorCount = $OtherCount; pid = $null; launchLog = $null
        launchRecord = $null; preparation = $null; startupEvidence = $null; mcpServerPid = $null
        blockers = @($Blockers)
    }
}

function Stop-UnverifiedUnityLaunch {
    param(
        [Parameter(Mandatory = $true)]$Process,
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [int[]]$PreexistingMcpProcessIds = @(),
        [Parameter(Mandatory = $true)][string]$Reason
    )

    $cleanupBlockers = @()
    $mcpRecord = Get-UnityMcpServerOwnershipRecord `
        -ProjectPath $ProjectPath `
        -Port 8080 `
        -PreexistingProcessIds $PreexistingMcpProcessIds `
        -NotBeforeUtc $Process.StartTime.ToUniversalTime()

    $editorStopped = $Process.HasExited
    if (-not $editorStopped) {
        try {
            Stop-Process -Id $Process.Id -ErrorAction Stop
            Wait-Process -Id $Process.Id -Timeout 30 -ErrorAction Stop
            $editorStopped = $true
        }
        catch {
            $cleanupBlockers += "The unverified Unity process did not exit cleanly; no forced termination was attempted."
        }
    }

    if ($mcpRecord -and $editorStopped) {
        $mcpCleanup = Stop-UnityMcpServerFromOwnershipRecord -Record $mcpRecord -TimeoutSec 15
        if (-not $mcpCleanup.ok) {
            $cleanupBlockers += @($mcpCleanup.blockers)
        }
    }
    elseif ($mcpRecord) {
        $cleanupBlockers += "The verified MCP server was left running because its Unity Editor did not exit cleanly."
    }

    return @($Reason) + @($cleanupBlockers)
}

function Test-LocalTcpPort {
    param([string]$HostName = "127.0.0.1", [int]$Port = 8080, [int]$TimeoutMs = 250)

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connect = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne($TimeoutMs)) { return $false }
        $client.EndConnect($connect)
        return $true
    }
    catch { return $false }
    finally { $client.Close() }
}

function Get-UnityVisibleWindowEvidence {
    param(
        [Parameter(Mandatory = $true)][int]$ProcessId,
        [Parameter(Mandatory = $true)][string]$ProjectPath
    )

    if ($IsWindows) {
        $candidate = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($candidate -and $candidate.MainWindowHandle -ne 0) {
            $kind = Get-UnityWindowEvidenceKind -Titles @($candidate.MainWindowTitle) -ProjectPath $ProjectPath
            if ($kind) { return [pscustomobject]@{ Found = $true; Kind = $kind } }
        }
        return [pscustomobject]@{ Found = $false; Kind = $null }
    }

    if (Test-UnityDebugMacOS) {
        $swift = Get-Command swift -ErrorAction SilentlyContinue
        if (-not $swift) { return [pscustomobject]@{ Found = $false; Kind = $null } }
        $swiftSource = @"
import CoreGraphics
let pid: Int32 = $ProcessId
let windows = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]) ?? []
for window in windows {
    if let owner = window[kCGWindowOwnerPID as String] as? Int32, owner == pid {
        print(window[kCGWindowName as String] as? String ?? "")
    }
}
"@
        $titles = @(& $swift.Source -e $swiftSource 2>$null)
        $kind = Get-UnityWindowEvidenceKind -Titles $titles -ProjectPath $ProjectPath
        if ($kind) { return [pscustomobject]@{ Found = $true; Kind = $kind } }
    }
    return [pscustomobject]@{ Found = $false; Kind = $null }
}

function Test-UnityMcpEvidence {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    if (-not (Test-LocalTcpPort)) { return $false }
    $powerShell = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
    if (-not $powerShell) { $powerShell = (Get-Command powershell -ErrorAction SilentlyContinue).Source }
    if (-not $powerShell) { return $false }
    & $powerShell -NoProfile -File (Join-Path $PSScriptRoot "Invoke-UnityMcpRecovery.ps1") -ProjectPath $ProjectPath -StatusOnly *> $null
    return $LASTEXITCODE -eq 0
}

function Invoke-PreparationProcess {
    param([string]$Project, [string]$Editor, [switch]$WhatIfOnly)
    $powerShell = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
    if (-not $powerShell) { $powerShell = (Get-Command powershell -ErrorAction SilentlyContinue).Source }
    if (-not $powerShell) { throw "PowerShell executable was not found for the isolated preparation step." }
    $arguments = @("-NoProfile", "-File", (Join-Path $PSScriptRoot "Prepare-UnityEditorLaunch.ps1"), "-ProjectPath", $Project, "-UnityPath", $Editor, "-TimeoutSec", [string]$PreparationTimeoutSec, "-AsJson")
    if ($WhatIfOnly) { $arguments += "-DryRun" }
    $output = & $powerShell @arguments
    $exitCode = $LASTEXITCODE
    try { $report = (($output | Out-String).Trim() | ConvertFrom-Json) } catch { throw "Preparation returned invalid structured output." }
    return [pscustomobject]@{ ExitCode = $exitCode; Report = $report }
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$repositoryRoot = Get-UnityDebugSkillBasePath
$permission = Get-UnityVisibleEditorLaunchPermission -RepositoryRoot $repositoryRoot
$projectEditors = @(Get-UnityProjectProcesses -ProjectPath $resolvedProjectPath)
$allEditors = @(Get-UnityEditorProcesses | Where-Object { -not $_.IsBatchMode })
$otherEditors = @($allEditors | Where-Object { -not (Test-UnityPathEqual $_.ProjectPath $resolvedProjectPath) })
$memory = Get-UnityAvailableMemory
$memoryGate = Test-UnityEditorMemoryGate -Memory $memory -OtherEditorCount $otherEditors.Count -MinimumAvailableMemoryGB $MinimumAvailableMemoryGB
$blockers = @()
if (-not $permission.Allowed) { $blockers += "The repository configuration does not allow the Agent to launch a visible Unity Editor." }
if ($projectEditors.Count -gt 0) { $blockers += "The exact project is already open. Reuse that Editor; launch permission does not restrict controlling it." }
if (-not $memoryGate.Allowed -and -not ($ForceLowMemory -and $memory.Succeeded -and $otherEditors.Count -gt 0)) { $blockers += $memoryGate.Reason }

if ([string]::IsNullOrWhiteSpace($UnityPath)) { $UnityPath = Get-ConfiguredUnityPath }
$resolvedUnityPath = if ($UnityPath) { Resolve-UnityExecutablePath -Path $UnityPath } else { $null }
if (-not $resolvedUnityPath) { $blockers += "Unity executable is not configured or does not exist." }
$resolvedScenePath = Join-Path $resolvedProjectPath $ScenePath
if (-not (Test-Path -LiteralPath $resolvedScenePath -PathType Leaf)) { $blockers += "Scene was not found: $resolvedScenePath" }

$result = New-LaunchResult -Project $resolvedProjectPath -Memory $memory -OtherCount $otherEditors.Count -Blockers $blockers
$result.permission = $permission
if ($blockers.Count -gt 0) { Write-LaunchResult $result; exit 1 }

try {
    $preparation = Invoke-PreparationProcess -Project $resolvedProjectPath -Editor $resolvedUnityPath -WhatIfOnly:$DryRun
    $result.preparation = $preparation.Report
    if ($preparation.ExitCode -ne 0 -or -not $preparation.Report.ok) {
        $result.blockers = @("Mandatory batchmode preparation failed.") + @($preparation.Report.blockers)
        Write-LaunchResult $result
        exit 1
    }
}
catch {
    $result.blockers = @("Mandatory batchmode preparation failed: $($_.Exception.Message)")
    Write-LaunchResult $result
    exit 1
}

$tempDir = Join-Path $resolvedProjectPath "_temp"
$launchLog = Join-Path $tempDir ("UnityEditorAgentLaunch_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss_fff"))
$arguments = @("-projectPath", $resolvedProjectPath, "-openfile", $resolvedScenePath, "-logFile", $launchLog)
$result.launchLog = $launchLog
if ($DryRun) {
    $result.ok = $true
    $result | Add-Member -NotePropertyName arguments -NotePropertyValue @($arguments)
    Write-LaunchResult $result
    if (-not $AsJson) { Write-Host "[DRY RUN] $resolvedUnityPath $(Format-NativeArgumentList -ArgumentList $arguments)" }
    exit 0
}

# Recheck immediately before launch; preparation may have changed process and memory state.
$permission = Get-UnityVisibleEditorLaunchPermission -RepositoryRoot $repositoryRoot
$projectEditors = @(Get-UnityProjectProcesses -ProjectPath $resolvedProjectPath)
$otherEditors = @(Get-UnityEditorProcesses | Where-Object { -not $_.IsBatchMode -and -not (Test-UnityPathEqual $_.ProjectPath $resolvedProjectPath) })
$memory = Get-UnityAvailableMemory
$memoryGate = Test-UnityEditorMemoryGate -Memory $memory -OtherEditorCount $otherEditors.Count -MinimumAvailableMemoryGB $MinimumAvailableMemoryGB
$currentSource = Get-UnityLaunchSourceSnapshot -Root $resolvedProjectPath
$recheckBlockers = @()
if (-not $permission.Allowed) { $recheckBlockers += "Launch permission changed or could not be resolved after preparation." }
if ($projectEditors.Count -gt 0) { $recheckBlockers += "The project became owned by another Unity process during preparation." }
if (-not $memoryGate.Allowed -and -not ($ForceLowMemory -and $memory.Succeeded -and $otherEditors.Count -gt 0)) { $recheckBlockers += $memoryGate.Reason }
$validatedSource = $preparation.Report.sourceAfter
$sourceStillValidated = $validatedSource -and $currentSource.Path -and
    (Test-UnityPathEqual ([string]$validatedSource.Path) ([string]$currentSource.Path)) -and
    ([datetime]$validatedSource.LastWriteTimeUtc).ToUniversalTime() -eq ([datetime]$currentSource.LastWriteTimeUtc).ToUniversalTime()
if (-not $sourceStillValidated) { $recheckBlockers += "Relevant project source changed after mandatory preparation; launch requires a new preparation run." }
if ($recheckBlockers.Count -gt 0) {
    $result.permission = $permission; $result.memory = $memory; $result.otherEditorCount = $otherEditors.Count; $result.blockers = $recheckBlockers
    Write-LaunchResult $result
    exit 1
}

# A new listener can be owned only when it was absent immediately before this launch.
# Existing MCP servers remain outside this launch record and are never stopped by it.
$preexistingMcpProcessIds = @(Get-UnityDebugListeningProcessIds -Port 8080)

New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
try {
    $process = Start-UnityVisibleEditorProcess -FilePath $resolvedUnityPath -ArgumentList $arguments -ProjectPath $resolvedProjectPath -WorkingDirectory $resolvedProjectPath
}
catch {
    $result.blockers = @("Unity visible launch failed before exact-project process ownership could be established: $($_.Exception.Message). No ownership record was created.")
    Write-LaunchResult $result
    exit 1
}
$startupDeadline = (Get-Date).AddSeconds($StartupTimeoutSec)
$nextEvidenceProbe = Get-Date
$evidenceObservedAt = $null
$evidenceKind = $null
do {
    Start-Sleep -Milliseconds 500
    if ($process.HasExited) {
        $result.blockers = Stop-UnverifiedUnityLaunch -Process $process -ProjectPath $resolvedProjectPath -PreexistingMcpProcessIds $preexistingMcpProcessIds -Reason "Unity exited during bounded startup verification with code $($process.ExitCode). No ownership record was created; inspect the dedicated launch log."
        Write-LaunchResult $result
        exit 1
    }
    $ownedProcess = @(Get-UnityProjectProcesses -ProjectPath $resolvedProjectPath | Where-Object { $_.Id -eq $process.Id })
    if ($ownedProcess.Count -ne 1) {
        $result.blockers = Stop-UnverifiedUnityLaunch -Process $process -ProjectPath $resolvedProjectPath -PreexistingMcpProcessIds $preexistingMcpProcessIds -Reason "The launched PID stopped proving exact-project ownership during startup. No ownership record was created."
        Write-LaunchResult $result
        exit 1
    }

    if (-not $evidenceObservedAt -and (Get-Date) -ge $nextEvidenceProbe) {
        $windowEvidence = Get-UnityVisibleWindowEvidence -ProcessId $process.Id -ProjectPath $resolvedProjectPath
        if ($windowEvidence.Found -and $windowEvidence.Kind -eq "safe-mode-window") {
            $evidenceObservedAt = Get-Date
            $evidenceKind = $windowEvidence.Kind
        }
        elseif (Test-UnityMcpEvidence -ProjectPath $resolvedProjectPath) {
            $evidenceObservedAt = Get-Date
            $evidenceKind = "mcp-read-console"
        }
        $nextEvidenceProbe = (Get-Date).AddSeconds(2)
    }

    $evidenceStableSeconds = if ($evidenceObservedAt) { ((Get-Date) - $evidenceObservedAt).TotalSeconds } else { 0 }
    $startupReady = Test-UnityStartupReadinessState -ProcessAlive:(-not $process.HasExited) -ExactProjectOwned:($ownedProcess.Count -eq 1) -HasAutomationReadyEvidence:($null -ne $evidenceObservedAt) -EvidenceStableSeconds $evidenceStableSeconds -RequiredStableSeconds $StartupStabilitySec
} while (-not $startupReady -and (Get-Date) -lt $startupDeadline)

if (-not $startupReady) {
    $result.blockers = Stop-UnverifiedUnityLaunch -Process $process -ProjectPath $resolvedProjectPath -PreexistingMcpProcessIds $preexistingMcpProcessIds -Reason "Unity did not provide sustained exact-project MCP evidence or an exact-PID Safe Mode window within $StartupTimeoutSec seconds. A normal project window alone is not automation-ready. No ownership record was created."
    Write-LaunchResult $result
    exit 1
}

$mcpServerRecord = Get-UnityMcpServerOwnershipRecord `
    -ProjectPath $resolvedProjectPath `
    -Port 8080 `
    -PreexistingProcessIds $preexistingMcpProcessIds `
    -NotBeforeUtc $process.StartTime.ToUniversalTime()
if ($evidenceKind -eq "mcp-read-console" -and $preexistingMcpProcessIds.Count -eq 0 -and -not $mcpServerRecord) {
    $result.blockers = Stop-UnverifiedUnityLaunch -Process $process -ProjectPath $resolvedProjectPath -PreexistingMcpProcessIds $preexistingMcpProcessIds -Reason "MCP became ready through a newly started listener, but strong project-scoped server ownership could not be established. No launch record was created."
    Write-LaunchResult $result
    exit 1
}

$recordPath = Join-Path $tempDir ("UnityEditorAgentLaunch_{0}.json" -f $process.Id)
$record = [ordered]@{
    schemaVersion = 1; pid = $process.Id; projectPath = $resolvedProjectPath; unityPath = $resolvedUnityPath
    processStartTimeUtc = $process.StartTime.ToUniversalTime().ToString("o")
    launchedAtUtc = (Get-Date).ToUniversalTime().ToString("o"); launchLog = $launchLog; owner = "agent"
}
if ($mcpServerRecord) { $record.mcpServer = $mcpServerRecord }
Write-UnityDebugJson -Path $recordPath -Value $record
$result.ok = $true; $result.permission = $permission; $result.memory = $memory; $result.otherEditorCount = $otherEditors.Count
$result.pid = $process.Id; $result.launchRecord = $recordPath; $result.startupEvidence = $evidenceKind
$result.mcpServerPid = if ($mcpServerRecord) { [int]$mcpServerRecord.pid } else { $null }
$result.blockers = @()
Write-LaunchResult $result
