[CmdletBinding()]
param(
    [string]$ProjectPath = (Join-Path $PSScriptRoot '../..'),
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^M07-Baseline-[A-Za-z0-9._-]+$')]
    [string]$BaselineId,
    [ValidateRange(1, 86400)][int]$TimeoutSec = 28800,
    [string]$BuildTarget = 'StandaloneOSX',
    [string]$ResourceOutput,
    [string]$NativeOnOutput,
    [string]$NativeOffOutput,
    [switch]$ControlledFailureAfterValidateCompilerInputs
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/../../.agents/skills/unity-debug/scripts/UnityDebug.Common.ps1"

function Get-M07OuterHash {
    param([byte[]]$Bytes)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Save-M07WorkflowInputs {
    param([string]$Project, [string]$Root)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot snapshot M07 workflow inputs while this project is open.' }
    $specs = @(
        @{ relative = 'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity'; backup = 'm07-bootstrap-scene.original' },
        @{ relative = 'ProjectSettings/AssemblyShadowSettings.asset'; backup = 'assembly-shadow-settings.original' },
        @{ relative = 'ProjectSettings/EditorBuildSettings.asset'; backup = 'editor-build-settings.original' }
    )
    $rows = @()
    foreach ($spec in $specs) {
        $path = [IO.Path]::GetFullPath((Join-Path $Project $spec.relative))
        if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (([IO.File]::GetAttributes($path) -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "M07 workflow input is missing or linked: $($spec.relative)"
        }
        $bytes = [IO.File]::ReadAllBytes($path)
        $backup = Join-Path $Root $spec.backup
        $stream = [IO.File]::Open($backup, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) }
        finally { $stream.Dispose() }
        $rows += [pscustomobject]@{ relative = $spec.relative; backup = $backup; originalSha256 = Get-M07OuterHash $bytes }
    }
    return @($rows)
}

function Restore-M07WorkflowInputs {
    param([string]$Project, [string]$Root, [object[]]$State)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot restore M07 workflow inputs until every owned Unity process exits.' }
    if ($State.Count -ne 3) { throw 'M07 workflow input snapshot is incomplete.' }
    $rows = @()
    foreach ($entry in $State) {
        $path = [IO.Path]::GetFullPath((Join-Path $Project $entry.relative))
        $backup = [IO.Path]::GetFullPath($entry.backup)
        if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { throw "M07 workflow backup is missing: $($entry.relative)" }
        $original = [IO.File]::ReadAllBytes($backup)
        if ((Get-M07OuterHash $original) -cne $entry.originalSha256) { throw "M07 workflow backup changed: $($entry.relative)" }
        $current = [IO.File]::ReadAllBytes($path)
        $beforeRestore = Join-Path $Root (([IO.Path]::GetFileName($backup)) + '.before-restore')
        $evidence = [IO.File]::Open($beforeRestore, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $evidence.Write($current, 0, $current.Length); $evidence.Flush($true) }
        finally { $evidence.Dispose() }
        $stream = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
        try {
            $stream.Position = 0
            $stream.Write($original, 0, $original.Length)
            $stream.SetLength($original.Length)
            $stream.Flush($true)
        }
        finally { $stream.Dispose() }
        $restored = [IO.File]::ReadAllBytes($path)
        $restoredSha = Get-M07OuterHash $restored
        if ($restoredSha -cne $entry.originalSha256) { throw "M07 workflow exact-byte restore failed: $($entry.relative)" }
        $rows += [ordered]@{
            path = $entry.relative
            originalSha256 = $entry.originalSha256
            beforeRestoreSha256 = Get-M07OuterHash $current
            restoredSha256 = $restoredSha
        }
    }
    $receipt = [ordered]@{ schemaVersion = 1; kind = 'M07OuterFailureRestoration'; status = 'ExactBytesRestored'; files = $rows }
    $receiptPath = Join-Path $Root 'workflow-inputs-restored.json'
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes(($receipt | ConvertTo-Json -Depth 6) + "`n")
    $file = [IO.File]::Open($receiptPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $file.Write($bytes, 0, $bytes.Length); $file.Flush($true) }
    finally { $file.Dispose() }
}

function Assert-M07ControlledPinnedInputs {
    param([string]$Project)
    $python = Get-Command python3 -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $python) { $python = Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1 }
    if (-not $python) { throw 'Python is required to verify the real pinned M07 build inputs.' }
    & $python.Source (Join-Path $Project 'Tools/AssemblyShadow/verify-installed-runtime.py') --project $Project --expect-shadow on --json
    if ($LASTEXITCODE -ne 0) { throw 'Controlled M07 validation source or installation differs from the pinned build inputs.' }
}

function Invoke-M07ControlledValidateCompilerInputs {
    param([string]$Project, [string]$Baseline, [int]$Timeout, [string]$Target)
    $methodScript = Join-Path $Project '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
    if (-not (Test-Path -LiteralPath $methodScript -PathType Leaf)) { throw "Shared Unity method launcher missing: $methodScript" }
    $payload = @{ method = 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs'; project = $Project; script = $methodScript;
        timeout = $Timeout; target = $Target; arguments = @('-shadowBaselineId', $Baseline) } | ConvertTo-Json -Compress
    $data = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
    $command = '$ErrorActionPreference = ''Stop''; $p = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(''' + $data + ''')) | ConvertFrom-Json; ' +
        '$invoke = @{ Method = $p.method; ProjectPath = $p.project; TimeoutSec = $p.timeout; MethodArgs = @($p.arguments) }; ' +
        'if ($p.target) { $invoke.BuildTarget = $p.target }; & $p.script @invoke'
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $powerShell = (Get-Process -Id $PID).Path
    & $powerShell -NoLogo -NoProfile -NonInteractive -OutputFormat Text -EncodedCommand $encoded
    if ($LASTEXITCODE -ne 0) { throw "Controlled M07 ValidateCompilerInputs failed (PowerShell/Unity exit $LASTEXITCODE)." }
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Controlled M07 ValidateCompilerInputs returned before its Unity process exited.' }
}

$shadowProject = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'This exact project is already open in Unity; no M07 workflow was started.' }
$evidenceParent = Join-Path $shadowProject '_temp/AssemblyShadow'
New-Item -ItemType Directory -Force -Path $evidenceParent | Out-Null
$recoveryRoot = Join-Path $evidenceParent ('M07OuterRecovery-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $recoveryRoot | Out-Null
$state = Save-M07WorkflowInputs -Project $shadowProject -Root $recoveryRoot
$core = Join-Path $PSScriptRoot 'Invoke-M07Build.Core.ps1'
if (-not (Test-Path -LiteralPath $core -PathType Leaf)) { throw "M07 core workflow is missing: $core" }
$invoke = @{
    ProjectPath = $shadowProject
    BaselineId = $BaselineId
    TimeoutSec = $TimeoutSec
    BuildTarget = $BuildTarget
}
if ($ResourceOutput) { $invoke.ResourceOutput = $ResourceOutput }
if ($NativeOnOutput) { $invoke.NativeOnOutput = $NativeOnOutput }
if ($NativeOffOutput) { $invoke.NativeOffOutput = $NativeOffOutput }

$workflowFailure = $null
$restoreFailure = $null
try {
    if ($ControlledFailureAfterValidateCompilerInputs) {
        Assert-M07ControlledPinnedInputs -Project $shadowProject
        Invoke-M07ControlledValidateCompilerInputs -Project $shadowProject -Baseline $BaselineId -Timeout $TimeoutSec -Target $BuildTarget
        Assert-M07ControlledPinnedInputs -Project $shadowProject
        throw 'Controlled M07 failure after successful ValidateCompilerInputs for exact-byte restoration verification.'
    }
    & $core @invoke
}
catch {
    $workflowFailure = $_
}
finally {
    if ($workflowFailure) {
        try { Restore-M07WorkflowInputs -Project $shadowProject -Root $recoveryRoot -State $state }
        catch { $restoreFailure = $_ }
    }
}
if ($restoreFailure) { throw "M07 workflow failed and outer exact-byte recovery also failed. Workflow: $workflowFailure Recovery: $restoreFailure" }
if ($workflowFailure) { throw $workflowFailure }
