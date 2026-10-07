[CmdletBinding()]
param(
    [string]$TestFilter = 'HybridCLR.Editor.AssemblyShadow.Tests',
    [int]$TimeoutSec = 1200
)

. "$PSScriptRoot/../../.agents/skills/unity-debug/scripts/UnityDebug.Common.ps1"

$shadowProject = Get-UnityDebugProjectPath
if (Test-UnityProjectRunning -ProjectPath $shadowProject) {
    throw 'This project is already open in Unity; do not start another instance.'
}
$shadowUnity = Get-ConfiguredUnityPath
if (-not $shadowUnity) { throw 'Configure the pinned Unity executable with Find-Unity first.' }
$shadowRun = Join-Path $shadowProject ("_temp/AssemblyShadow/EditorTests-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $shadowRun | Out-Null
$shadowXml = Join-Path $shadowRun 'results.xml'
$shadowLog = Join-Path $shadowRun 'unity.log'
$shadowArguments = @('-projectPath', $shadowProject, '-batchmode', '-runTests', '-testPlatform', 'EditMode', '-testFilter', $TestFilter, '-testResults', $shadowXml, '-logFile', $shadowLog)
Write-Host "Unity test output: $shadowRun"
$shadowProcess = Start-UnityNativeProcess -FilePath $shadowUnity -ArgumentList $shadowArguments -WorkingDirectory $shadowProject -Hidden
if (-not $shadowProcess.WaitForExit($TimeoutSec * 1000)) {
    Stop-Process -Id $shadowProcess.Id -Force -ErrorAction SilentlyContinue
    throw "Owned Unity test process timed out; log: $shadowLog"
}
if (-not (Test-Path -LiteralPath $shadowXml)) { throw "Unity emitted no test results (exit $($shadowProcess.ExitCode)); log: $shadowLog" }
[xml]$shadowResults = Get-Content -LiteralPath $shadowXml -Raw
$shadowSummary = $shadowResults.'test-run'
$shadowSummary | Select-Object result, total, passed, failed, skipped | ConvertTo-Json
if ($shadowProcess.ExitCode -ne 0 -or $shadowSummary.result -ne 'Passed' -or [int]$shadowSummary.total -eq 0 -or [int]$shadowSummary.failed -ne 0) {
    throw "Unity tests did not pass; result: $shadowXml; log: $shadowLog"
}
Write-Host "Passed. Results: $shadowXml"
