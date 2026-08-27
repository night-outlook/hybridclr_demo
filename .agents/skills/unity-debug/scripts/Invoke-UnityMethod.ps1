[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Method,
    [string[]]$MethodArgs,
    [string]$ProjectPath,
    [int]$TimeoutSec = 300,
    [string]$BuildTarget,
    [switch]$DryRun,
    [switch]$Status
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$version = Get-UnityEditorVersion -ProjectPath $resolvedProjectPath
Save-UnityDebugRepoConfig -ProjectPath $resolvedProjectPath -Version $version

if ($Status) {
    $running = Test-UnityProjectRunning -ProjectPath $resolvedProjectPath
    $unityPath = Get-ConfiguredUnityPath
    Write-Host "Project: $resolvedProjectPath"
    Write-Host "Unity version: $version"
    Write-Host ("Unity running for this project: {0}" -f ($(if ($running) { "yes" } else { "no" })))
    Write-Host ("Configured Unity executable: {0}" -f ($(if ($unityPath) { $unityPath } else { "not set" })))
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Method)) {
    Write-Error "Specify a method name, for example: Namespace.Class.Method"
    exit 1
}

if (Test-UnityProjectRunning -ProjectPath $resolvedProjectPath) {
    Write-Error "This project is already open in Unity. Close this project's Unity Editor before running -executeMethod."
    exit 1
}

$unityPath = Get-ConfiguredUnityPath
if (-not $unityPath) {
    Write-Error "Unity executable is not configured. Run .\.agents\skills\unity-debug\scripts\Find-Unity.ps1 first, or use -Set."
    exit 1
}

$tempDir = Join-Path $resolvedProjectPath "_temp"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$logFile = Join-Path $tempDir ("UnityExec_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

$arguments = @(
    "-projectPath", $resolvedProjectPath,
    "-batchmode",
    "-quit",
    "-logFile", $logFile,
    "-executeMethod", $Method
)

if ($BuildTarget) {
    $arguments += @("-buildTarget", $BuildTarget)
}
if ($MethodArgs) {
    $arguments += $MethodArgs
}

Write-Host "[INFO] Unity: $unityPath"
Write-Host "[INFO] Project: $resolvedProjectPath"
Write-Host "[INFO] Method: $Method"
Write-Host "[INFO] Log: $logFile"

if ($DryRun) {
    Write-Host "[DRY RUN] $unityPath $(Format-NativeArgumentList -ArgumentList $arguments)"
    exit 0
}

try {
    $process = Start-UnityNativeProcess -FilePath $unityPath -ArgumentList $arguments -WorkingDirectory $resolvedProjectPath -Hidden
    $completed = $process.WaitForExit($TimeoutSec * 1000)
    if (-not $completed) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw "Unity method execution timed out after $TimeoutSec seconds."
    }

    if ($process.ExitCode -eq 0) {
        Write-Host "[SUCCESS] Unity method completed."
    }
    else {
        Write-Host "[FAILED] Unity method failed. ExitCode=$($process.ExitCode)"
    }

    if (Test-Path -LiteralPath $logFile) {
        Write-Host ""
        Write-Host "=== Log Tail ==="
        Get-Content -Encoding UTF8 -LiteralPath $logFile -Tail 120
    }

    exit $process.ExitCode
}
catch {
    Write-Error $_
    exit 1
}
