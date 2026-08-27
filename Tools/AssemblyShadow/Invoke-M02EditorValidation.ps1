[CmdletBinding()]
param(
    [string]$ProjectPath = (Join-Path $PSScriptRoot '../..'),
    [ValidateRange(1, 86400)][int]$TimeoutSec = 1200,
    [string]$BuildTarget
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/../../.agents/skills/unity-debug/scripts/UnityDebug.Common.ps1"

function Invoke-M02GuardedMethod {
    param([string]$Method, [string]$Project, [string]$Run, [string]$MethodScript, [int]$Timeout, [string]$Target)
    $payload = @{ method = $Method; project = $Project; run = $Run; script = $MethodScript; timeout = $Timeout; target = $Target } | ConvertTo-Json -Compress
    $data = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
    # Invoke-UnityMethod uses exit. Isolate it so failures cannot exit this
    # wrapper before finally restores the recorded original scripting defines.
    $command = '$ErrorActionPreference = ''Stop''; $p = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(''' + $data + ''')) | ConvertFrom-Json; ' +
        '$invoke = @{ Method = $p.method; ProjectPath = $p.project; TimeoutSec = $p.timeout; MethodArgs = @(''-shadowValidationRoot'', $p.run) }; ' +
        'if ($p.target) { $invoke.BuildTarget = $p.target }; & $p.script @invoke'
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $powerShell = (Get-Process -Id $PID).Path
    & $powerShell -NoLogo -NoProfile -NonInteractive -OutputFormat Text -EncodedCommand $encoded
    if ($LASTEXITCODE -ne 0) { throw "$Method failed (PowerShell/Unity exit $LASTEXITCODE). Recovery state: $Run" }
}

function Get-M02BytesHash {
    param([byte[]]$Bytes)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Assert-M02RegularSettingsPath {
    param([string]$Path)
    foreach ($item in @($Path, [IO.Path]::GetDirectoryName($Path))) {
        if (-not (Test-Path -LiteralPath $item) -or (([IO.File]::GetAttributes($item) -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "Settings evidence must not traverse a filesystem link: $item"
        }
    }
}

function Save-M02OriginalSettings {
    param([string]$Project, [string]$Run)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot capture original settings while this project is open.' }
    $settingsPath = Join-Path $Project 'ProjectSettings/ProjectSettings.asset'
    Assert-M02RegularSettingsPath $settingsPath
    $source = [IO.File]::Open($settingsPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None)
    try {
        $backup = [IO.File]::Open((Join-Path $Run 'p05-project-settings.original'), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $source.CopyTo($backup); $backup.Flush($true) }
        finally { $backup.Dispose() }
    }
    finally { $source.Dispose() }
}

function Restore-M02OriginalSettingsBytes {
    param([string]$Project, [string]$Run)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot restore settings bytes until this exact project Editor has exited.' }
    $settingsPath = Join-Path $Project 'ProjectSettings/ProjectSettings.asset'
    $backupPath = Join-Path $Run 'p05-project-settings.original'
    Assert-M02RegularSettingsPath $settingsPath
    Assert-M02RegularSettingsPath $backupPath
    $original = [IO.File]::ReadAllBytes($backupPath)
    $originalSha = Get-M02BytesHash $original
    $settings = [IO.File]::Open($settingsPath, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        $buffer = [IO.MemoryStream]::new()
        try { $settings.CopyTo($buffer); $currentSha = Get-M02BytesHash $buffer.ToArray() }
        finally { $buffer.Dispose() }
        $statePath = Join-Path $Run 'p05-define-state.json'
        if (-not (Test-Path -LiteralPath $statePath)) {
            if ($currentSha -ne $originalSha) { throw 'Prepare created no recovery state, but settings bytes changed; refusing an unproven overwrite.' }
            return
        }
        $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
        $stateSha = Get-M02BytesHash ([IO.File]::ReadAllBytes($statePath))
        $restorePath = Join-Path $Run 'p05-restored.json'
        if (-not (Test-Path -LiteralPath $restorePath)) { throw 'The Unity Restore process did not produce a verified settings receipt.' }
        $restored = Get-Content -Raw -LiteralPath $restorePath | ConvertFrom-Json
        if ($state.schemaVersion -ne 2 -or $state.projectDirectory -cne $Project -or $state.runDirectory -cne $Run -or
            $state.originalSettingsSha256 -cne $originalSha -or $restored.schemaVersion -ne 2 -or
            $restored.stateSha256 -cne $stateSha -or $restored.originalDefines -cne $state.originalDefines -or
            $restored.originalSettingsSha256 -cne $originalSha -or $restored.restoredSettingsSha256 -cnotmatch '^[0-9a-f]{64}$') {
            throw 'Settings restoration evidence does not bind this run and original byte snapshot.'
        }
        $markerPath = Join-Path $Run 'p05-settings-restored.json'
        if (Test-Path -LiteralPath $markerPath) {
            $marker = Get-Content -Raw -LiteralPath $markerPath | ConvertFrom-Json
            if ($marker.schemaVersion -ne 1 -or $marker.stateSha256 -cne $stateSha -or $marker.originalSettingsSha256 -cne $originalSha -or
                $marker.restoredSettingsSha256 -cne $restored.restoredSettingsSha256 -or $currentSha -cne $originalSha) {
                throw 'Settings changed after their original bytes were restored.'
            }
            return
        }
        if ($currentSha -cne $restored.restoredSettingsSha256) { throw 'Settings changed after Unity Restore; refusing to overwrite concurrent edits.' }
        if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'This project opened before the guarded byte restore.' }
        # Unity has verified that ONLY the recorded target-map entry differs.
        # Check and replace under the same exclusive handle; retain the backup.
        $settings.Position = 0
        $settings.Write($original, 0, $original.Length)
        $settings.SetLength($original.Length)
        $settings.Flush($true)
        $receipt = @{ schemaVersion = 1; stateSha256 = $stateSha; originalSettingsSha256 = $originalSha;
            restoredSettingsSha256 = $restored.restoredSettingsSha256 } | ConvertTo-Json
        $receiptBytes = [Text.UTF8Encoding]::new($false).GetBytes($receipt)
        $markerFile = [IO.File]::Open($markerPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $markerFile.Write($receiptBytes, 0, $receiptBytes.Length); $markerFile.Flush($true) }
        finally { $markerFile.Dispose() }
    }
    finally { $settings.Dispose() }
}

function Invoke-M02ValidationStages {
    param([Parameter(Mandatory = $true)][scriptblock]$InvokeStage)
    $stageFailure = $null
    $restoreFailure = $null
    try {
        & $InvokeStage 'Prepare'
        & $InvokeStage 'Compile'
    }
    catch { $stageFailure = $_ }
    finally {
        try { & $InvokeStage 'Restore' }
        catch { $restoreFailure = $_ }
    }
    if ($restoreFailure) {
        throw "P05 recovery failed; do not continue validation. Original failure: $stageFailure Recovery failure: $restoreFailure"
    }
    if ($stageFailure) { throw $stageFailure }
    & $InvokeStage 'Validate'
}

$shadowProject = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$shadowMethods = Join-Path $shadowProject '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
if (-not (Test-Path -LiteralPath $shadowMethods -PathType Leaf)) { throw "Shared Unity method launcher missing: $shadowMethods" }
if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'This exact project is already open in Unity; no validation processes were started.' }
if (-not (Get-ConfiguredUnityPath)) { throw 'Configure the pinned Unity executable with Find-Unity first.' }
$shadowParent = Join-Path $shadowProject '_temp/AssemblyShadow'
New-Item -ItemType Directory -Force -Path $shadowParent | Out-Null
$shadowLockPath = Join-Path $shadowParent 'm02-editor-validation.lock'
$shadowLock = [IO.File]::Open($shadowLockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
try {
    # Hold one cross-process workflow lock across the gaps between Editors.
    if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'This project opened while acquiring the validation lock.' }
    $shadowRun = Join-Path $shadowParent ('M02Validation-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $shadowRun | Out-Null
    Write-Host "M02 validation run: $shadowRun"
    Save-M02OriginalSettings -Project $shadowProject -Run $shadowRun
    Invoke-M02ValidationStages -InvokeStage {
        param($stage)
        $method = if ($stage -eq 'Validate') { 'AssemblyShadowDemo.Editor.M02EditorValidation.Validate' }
            else { 'AssemblyShadowDemo.Editor.M02StructuralPatchCompilation.' + $stage }
        Invoke-M02GuardedMethod -Method $method -Project $shadowProject -Run $shadowRun -MethodScript $shadowMethods -Timeout $TimeoutSec -Target $BuildTarget
        if ($stage -eq 'Restore') { Restore-M02OriginalSettingsBytes -Project $shadowProject -Run $shadowRun }
    }
    if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'The final validation Editor has not exited.' }
    if ((Get-M02BytesHash ([IO.File]::ReadAllBytes((Join-Path $shadowProject 'ProjectSettings/ProjectSettings.asset')))) -cne
        (Get-M02BytesHash ([IO.File]::ReadAllBytes((Join-Path $shadowRun 'p05-project-settings.original'))))) {
        throw 'Final validation changed project settings; original bytes remain archived and were not blindly overwritten.'
    }
    Write-Host "M02 validation completed with original scripting defines restored: $shadowRun"
}
finally { $shadowLock.Dispose() }
