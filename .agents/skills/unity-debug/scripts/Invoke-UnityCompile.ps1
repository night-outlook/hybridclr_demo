[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string[]]$ChangedPath,
    [int]$TimeoutSec = 300,
    [switch]$CheckOnly,
    [switch]$Status,
    [switch]$AsJson,
    [switch]$FailOnStale,
    [switch]$DryRun
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

function Invoke-UnityBatchmode {
    param(
        [Parameter(Mandatory = $true)][string]$UnityPath,
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [Parameter(Mandatory = $true)][string]$LogFile,
        [Parameter(Mandatory = $true)][int]$TimeoutSec
    )

    $arguments = @(
        "-projectPath", $ProjectPath,
        "-batchmode",
        "-quit",
        "-logFile", $LogFile
    )

    if (-not $AsJson) {
        Write-Host "[INFO] Unity: $UnityPath"
        Write-Host "[INFO] Project: $ProjectPath"
        Write-Host "[INFO] Log: $LogFile"
    }

    $process = Start-UnityNativeProcess -FilePath $UnityPath -ArgumentList $arguments -WorkingDirectory $ProjectPath -Hidden
    $completed = $process.WaitForExit($TimeoutSec * 1000)
    if (-not $completed) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Unity compile timed out after $TimeoutSec seconds."
    }

    return $process.ExitCode
}

function New-UnityCompileReport {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [Parameter(Mandatory = $true)][string]$Version,
        [Parameter(Mandatory = $true)][bool]$UnityRunning,
        [Parameter(Mandatory = $true)][string]$Mode,
        [Parameter(Mandatory = $true)]$Errors,
        [string]$UnityPath,
        [object]$UnityExitCode,
        [bool]$BatchmodeCompileError,
        [string[]]$ChangedPath
    )

    $compilerErrorCount = @($Errors.CompilerErrors).Count + @($Errors.BatchmodeErrors).Count
    $consoleErrorCount = @($Errors.ConsoleErrors).Count
    $ignoredConsoleNoiseCount = @($Errors.IgnoredConsoleErrors).Count
    $verificationMessages = @()
    if ($Errors.EditorCompilerVerification) {
        $verificationMessages += $Errors.EditorCompilerVerification
    }
    if ($Errors.BatchmodeCompileVerification) {
        $verificationMessages += $Errors.BatchmodeCompileVerification
    }

    $staleLogNotices = @($Errors.StaleLogNotices)
    $runtimeStaleLogNotices = @($Errors.RuntimeStaleLogNotices)
    $isStale = $verificationMessages.Count -gt 0 -or $staleLogNotices.Count -gt 0
    $actionableConsoleErrorCount = Get-UnityDebugActionableConsoleErrorCount -ConsoleErrors $Errors.ConsoleErrors -RuntimeStaleLogNotices $runtimeStaleLogNotices
    $hasErrors = $compilerErrorCount -gt 0 -or $actionableConsoleErrorCount -gt 0 -or $BatchmodeCompileError
    if ($null -ne $UnityExitCode -and [int]$UnityExitCode -ne 0) {
        $hasErrors = $true
    }

    $failureReasons = @()
    if ($hasErrors) {
        $failureReasons += "errors"
    }
    if ($FailOnStale -and $isStale) {
        $failureReasons += "stale"
    }

    return [pscustomobject]@{
        ok = ($failureReasons.Count -eq 0)
        mode = $Mode
        projectPath = $ProjectPath
        unityVersion = $Version
        unityRunning = $UnityRunning
        configuredUnityPath = $UnityPath
        unityExitCode = $(if ($null -ne $UnityExitCode) { [int]$UnityExitCode } else { $null })
        changedPath = @($ChangedPath)
        compilerErrorCount = $compilerErrorCount
        consoleErrorCount = $consoleErrorCount
        actionableConsoleErrorCount = $actionableConsoleErrorCount
        ignoredConsoleNoiseCount = $ignoredConsoleNoiseCount
        hasErrors = $hasErrors
        isStale = $isStale
        failOnStale = [bool]$FailOnStale
        failureReasons = @($failureReasons)
        editorCompilerVerification = $Errors.EditorCompilerVerification
        batchmodeCompileVerification = $Errors.BatchmodeCompileVerification
        staleLogNotices = @($staleLogNotices)
        runtimeStaleLogNotices = @($runtimeStaleLogNotices)
        isRuntimeLogStale = $runtimeStaleLogNotices.Count -gt 0
        compilerLog = $Errors.CompilerLog
        consoleLog = $Errors.ConsoleLog
        batchmodeLog = $Errors.BatchmodeLog
        compilerLogLastWriteTime = $Errors.CompilerLogLastWriteTime
        consoleLogLastWriteTime = $Errors.ConsoleLogLastWriteTime
        batchmodeLogLastWriteTime = $Errors.BatchmodeLogLastWriteTime
        recentRelevantEditPath = $Errors.RecentRelevantEditPath
        recentRelevantEditLastWriteTime = $Errors.RecentRelevantEditLastWriteTime
        reproMarkerPath = $Errors.ReproMarkerPath
        reproMarkerStartedAt = $Errors.ReproMarkerStartedAt
        compilerErrors = @($Errors.CompilerErrors)
        batchmodeErrors = @($Errors.BatchmodeErrors)
        consoleErrors = @($Errors.ConsoleErrors)
        ignoredConsoleErrors = @($Errors.IgnoredConsoleErrors)
    }
}

function Write-UnityCompileReport {
    param(
        [Parameter(Mandatory = $true)]$Report,
        [Parameter(Mandatory = $true)]$Errors
    )

    if ($AsJson) {
        $Report | ConvertTo-Json -Depth 12
    }
    else {
        Write-UnityDebugErrors -Errors $Errors
    }
}

function Get-UnityCompileReportExitCode {
    param([Parameter(Mandatory = $true)]$Report)

    if ($Report.hasErrors) {
        return 1
    }
    if ($FailOnStale -and $Report.isStale) {
        return 2
    }
    return 0
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$version = Get-UnityEditorVersion -ProjectPath $resolvedProjectPath
Save-UnityDebugRepoConfig -ProjectPath $resolvedProjectPath -Version $version
$isUnityRunning = Test-UnityProjectRunning -ProjectPath $resolvedProjectPath

if ($Status) {
    $unityPath = Get-ConfiguredUnityPath
    $errors = Get-UnityDebugErrorLines -ProjectPath $resolvedProjectPath -IncludeEditorCompilerLog:$isUnityRunning -IncludeBatchmodeCompileLog:(!$isUnityRunning) -ChangedPath $ChangedPath
    $report = New-UnityCompileReport -ProjectPath $resolvedProjectPath -Version $version -UnityRunning $isUnityRunning -Mode "status" -Errors $errors -UnityPath $unityPath -UnityExitCode $null -BatchmodeCompileError:$false -ChangedPath $ChangedPath
    if ($AsJson) {
        Write-UnityCompileReport -Report $report -Errors $errors
    }
    else {
        Write-Host "Project: $resolvedProjectPath"
        Write-Host "Unity version: $version"
        Write-Host ("Unity running for this project: {0}" -f ($(if ($isUnityRunning) { "yes" } else { "no" })))
        Write-Host ("Configured Unity executable: {0}" -f ($(if ($unityPath) { $unityPath } else { "not set" })))
        Write-Host ""
        Write-UnityCompileReport -Report $report -Errors $errors
    }
    if ($FailOnStale) {
        exit (Get-UnityCompileReportExitCode -Report $report)
    }
    exit 0
}

if ($CheckOnly) {
    $errors = Get-UnityDebugErrorLines -ProjectPath $resolvedProjectPath -IncludeEditorCompilerLog:$isUnityRunning -IncludeBatchmodeCompileLog:(!$isUnityRunning) -ChangedPath $ChangedPath
    $report = New-UnityCompileReport -ProjectPath $resolvedProjectPath -Version $version -UnityRunning $isUnityRunning -Mode "check" -Errors $errors -UnityPath (Get-ConfiguredUnityPath) -UnityExitCode $null -BatchmodeCompileError:$false -ChangedPath $ChangedPath
    Write-UnityCompileReport -Report $report -Errors $errors
    exit (Get-UnityCompileReportExitCode -Report $report)
}

if ($isUnityRunning) {
    $errors = Get-UnityDebugErrorLines -ProjectPath $resolvedProjectPath -IncludeEditorCompilerLog -ChangedPath $ChangedPath
    $report = New-UnityCompileReport -ProjectPath $resolvedProjectPath -Version $version -UnityRunning $isUnityRunning -Mode "running-editor-blocked" -Errors $errors -UnityPath (Get-ConfiguredUnityPath) -UnityExitCode $null -BatchmodeCompileError:$false -ChangedPath $ChangedPath
    if ($AsJson) {
        Write-UnityCompileReport -Report $report -Errors $errors
    }
    else {
        Write-Host "[WARN] This project is already open in Unity; batchmode compile is not safe."
        Write-Host "[INFO] Showing existing error logs instead."
        Write-Host ""
        Write-UnityCompileReport -Report $report -Errors $errors
    }
    exit 1
}

$unityPath = Get-ConfiguredUnityPath
if (-not $unityPath) {
    Write-Error "Unity executable is not configured. Run .\.agents\skills\unity-debug\scripts\Find-Unity.ps1 first, or use -Set."
    exit 1
}

if ($DryRun) {
    $dryLog = Join-Path $resolvedProjectPath "_temp/UnityCompile_DRYRUN.log"
    $dryArguments = @("-projectPath", $resolvedProjectPath, "-batchmode", "-quit", "-logFile", $dryLog)
    if ($AsJson) {
        [pscustomobject]@{ ok = $true; dryRun = $true; projectPath = $resolvedProjectPath; unityPath = $unityPath; arguments = $dryArguments; logFile = $dryLog } | ConvertTo-Json -Depth 6
    }
    else {
        Write-Host "[DRY RUN] $unityPath $(Format-NativeArgumentList -ArgumentList $dryArguments)"
    }
    exit 0
}

$tempDir = Join-Path $resolvedProjectPath "_temp"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$logFile = Join-Path $tempDir ("UnityCompile_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

try {
    $exitCode = Invoke-UnityBatchmode -UnityPath $unityPath -ProjectPath $resolvedProjectPath -LogFile $logFile -TimeoutSec $TimeoutSec
    Save-UnityDebugLastCompilation

    $logText = if (Test-Path -LiteralPath $logFile) { Get-Content -Raw -Encoding UTF8 -LiteralPath $logFile } else { "" }
    $hasCompileError = $logText -match "error CS\d+|Compilation failed|Compiler errors"

    if (-not $AsJson) {
        if ($exitCode -eq 0 -and -not $hasCompileError) {
            Write-Host "[SUCCESS] Unity batchmode compile completed."
        }
        else {
            Write-Host "[FAILED] Unity batchmode compile reported errors. ExitCode=$exitCode"
        }
    }

    $errors = Get-UnityDebugErrorLines -ProjectPath $resolvedProjectPath -IncludeBatchmodeCompileLog -ChangedPath $ChangedPath
    $report = New-UnityCompileReport -ProjectPath $resolvedProjectPath -Version $version -UnityRunning $isUnityRunning -Mode "batchmode" -Errors $errors -UnityPath $unityPath -UnityExitCode $exitCode -BatchmodeCompileError:$hasCompileError -ChangedPath $ChangedPath
    if ($AsJson) {
        Write-UnityCompileReport -Report $report -Errors $errors
    }
    else {
        Write-Host ""
        Write-UnityCompileReport -Report $report -Errors $errors
    }

    if (-not $AsJson -and ($exitCode -ne 0 -or $hasCompileError) -and $logText) {
        Write-Host ""
        Write-Host "=== Log Tail ==="
        Get-Content -Encoding UTF8 -LiteralPath $logFile -Tail 120
    }

    exit (Get-UnityCompileReportExitCode -Report $report)
}
catch {
    Write-Error $_
    exit 1
}
