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
    [string]$NativeOffOutput
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/../../.agents/skills/unity-debug/scripts/UnityDebug.Common.ps1"

function Get-M07BytesHash {
    param([byte[]]$Bytes)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Assert-M07RegularPath {
    param([string]$Path, [switch]$AllowMissingLeaf)
    $full = [IO.Path]::GetFullPath($Path)
    $items = if ($AllowMissingLeaf) { @([IO.Path]::GetDirectoryName($full)) } else { @($full, [IO.Path]::GetDirectoryName($full)) }
    foreach ($item in $items) {
        if (-not (Test-Path -LiteralPath $item) -or (([IO.File]::GetAttributes($item) -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "M07 evidence must not traverse a filesystem link: $item"
        }
    }
    return $full
}

function Assert-M07NewChild {
    param([string]$Path, [string]$Root, [string]$Label)
    $full = [IO.Path]::GetFullPath($Path)
    $parent = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($parent, [StringComparison]::Ordinal) -or (Test-Path -LiteralPath $full)) {
        throw "$Label must be a new path below $Root : $full"
    }
    Assert-M07RegularPath -Path $full -AllowMissingLeaf | Out-Null
    return $full
}

function Invoke-M07GuardedMethod {
    param([string]$Method, [string]$Project, [string]$MethodScript, [int]$Timeout, [string]$Target, [string[]]$Arguments)
    $payload = @{ method = $Method; project = $Project; script = $MethodScript; timeout = $Timeout; target = $Target; arguments = $Arguments } |
        ConvertTo-Json -Compress
    $data = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
    # Invoke-UnityMethod terminates its host with exit. Run it in an owned child
    # PowerShell so the outer workflow can always perform structural recovery.
    $command = '$ErrorActionPreference = ''Stop''; $p = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(''' + $data + ''')) | ConvertFrom-Json; ' +
        '$invoke = @{ Method = $p.method; ProjectPath = $p.project; TimeoutSec = $p.timeout; MethodArgs = @($p.arguments) }; ' +
        'if ($p.target) { $invoke.BuildTarget = $p.target }; & $p.script @invoke'
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $powerShell = (Get-Process -Id $PID).Path
    & $powerShell -NoLogo -NoProfile -NonInteractive -OutputFormat Text -EncodedCommand $encoded
    if ($LASTEXITCODE -ne 0) { throw "$Method failed (PowerShell/Unity exit $LASTEXITCODE)." }
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw "$Method returned before its Unity process exited." }
}

function Save-M07OriginalSettings {
    param([string]$Project, [string]$Run)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot capture ProjectSettings while this exact project is open.' }
    $settingsPath = Assert-M07RegularPath (Join-Path $Project 'ProjectSettings/ProjectSettings.asset')
    $source = [IO.File]::Open($settingsPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None)
    try {
        $backup = [IO.File]::Open((Join-Path $Run 'p05-project-settings.original'), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $source.CopyTo($backup); $backup.Flush($true) }
        finally { $backup.Dispose() }
    }
    finally { $source.Dispose() }
}

function Restore-M07OriginalSettingsBytes {
    param([string]$Project, [string]$Run)
    if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'Cannot restore settings bytes until the structural Editor exits.' }
    $settingsPath = Assert-M07RegularPath (Join-Path $Project 'ProjectSettings/ProjectSettings.asset')
    $backupPath = Assert-M07RegularPath (Join-Path $Run 'p05-project-settings.original')
    $original = [IO.File]::ReadAllBytes($backupPath)
    $originalSha = Get-M07BytesHash $original
    $settings = [IO.File]::Open($settingsPath, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    try {
        $buffer = [IO.MemoryStream]::new()
        try { $settings.CopyTo($buffer); $currentSha = Get-M07BytesHash $buffer.ToArray() }
        finally { $buffer.Dispose() }
        $statePath = Join-Path $Run 'p05-define-state.json'
        if (-not (Test-Path -LiteralPath $statePath)) {
            if ($currentSha -cne $originalSha) { throw 'Prepare left no recovery state but settings bytes changed; refusing an unproven overwrite.' }
            return
        }
        $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
        $stateSha = Get-M07BytesHash ([IO.File]::ReadAllBytes($statePath))
        $restorePath = Join-Path $Run 'p05-restored.json'
        if (-not (Test-Path -LiteralPath $restorePath)) { throw 'The Unity Restore process produced no verified settings receipt.' }
        $restored = Get-Content -Raw -LiteralPath $restorePath | ConvertFrom-Json
        if ($state.schemaVersion -ne 2 -or $state.projectDirectory -cne $Project -or $state.runDirectory -cne $Run -or
            $state.originalSettingsSha256 -cne $originalSha -or $restored.schemaVersion -ne 2 -or
            $restored.stateSha256 -cne $stateSha -or $restored.originalDefines -cne $state.originalDefines -or
            $restored.originalSettingsSha256 -cne $originalSha -or $restored.restoredSettingsSha256 -cnotmatch '^[0-9a-f]{64}$') {
            throw 'Settings restoration evidence does not bind this M07 run and its original bytes.'
        }
        $markerPath = Join-Path $Run 'p05-settings-restored.json'
        if (Test-Path -LiteralPath $markerPath) {
            $marker = Get-Content -Raw -LiteralPath $markerPath | ConvertFrom-Json
            if ($marker.schemaVersion -ne 1 -or $marker.stateSha256 -cne $stateSha -or $marker.originalSettingsSha256 -cne $originalSha -or
                $marker.restoredSettingsSha256 -cne $restored.restoredSettingsSha256 -or $currentSha -cne $originalSha) {
                throw 'ProjectSettings changed after the recorded exact-byte restore.'
            }
            return
        }
        if ($currentSha -cne $restored.restoredSettingsSha256) { throw 'Settings changed after Unity Restore; refusing to overwrite concurrent edits.' }
        if (Test-UnityProjectRunning -ProjectPath $Project) { throw 'This project opened before the guarded byte restore.' }
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

function Find-M07PlayerReceipt {
    param([string]$Project, [string]$Variant, [string]$Output, [string[]]$ExcludedPaths = @())
    $excluded = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($path in $ExcludedPaths) { [void]$excluded.Add([IO.Path]::GetFullPath($path)) }
    $matches = @()
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $Project '_temp/AssemblyShadow') -Filter 'm07-player-build.json' -File -Recurse) {
        $fullPath = [IO.Path]::GetFullPath($file.FullName)
        if ($excluded.Contains($fullPath)) { continue }
        try { $receipt = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json }
        catch { continue }
        if ($receipt.milestone -ceq 'M07' -and $receipt.variant -ceq $Variant -and
            $receipt.baselineBuildId -ceq $BaselineId -and $receipt.playerOutput -ceq $Output) { $matches += $fullPath }
    }
    if ($matches.Count -ne 1) { throw "Expected exactly one $Variant receipt for $Output; found $($matches.Count)." }
    return [IO.Path]::GetFullPath($matches[0])
}

$shadowProject = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$shadowMethods = Join-Path $shadowProject '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
if (-not (Test-Path -LiteralPath $shadowMethods -PathType Leaf)) { throw "Shared Unity method launcher missing: $shadowMethods" }
if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'This exact project is already open in Unity; no M07 process was started.' }
if (-not (Get-ConfiguredUnityPath)) { throw 'Configure the pinned Unity executable with Find-Unity first.' }

$parent = Join-Path $shadowProject '_temp/AssemblyShadow'
New-Item -ItemType Directory -Force -Path $parent | Out-Null
$existingPlayerReceipts = @(Get-ChildItem -LiteralPath $parent -Filter 'm07-player-build.json' -File -Recurse | ForEach-Object { [IO.Path]::GetFullPath($_.FullName) })
# M07 deliberately reuses M02StructuralPatchCompilation's crash-safe state
# machine, whose persisted contract requires this exact directory prefix.
$run = Join-Path $parent ('M02Validation-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run | Out-Null
$resourceRoot = Assert-M07NewChild ($(if ($ResourceOutput) { $ResourceOutput } else { Join-Path $parent ('M07ResourceBaseline-' + $BaselineId + '-' + [guid]::NewGuid().ToString('N')) })) $parent 'Resource output'
$buildRoot = Join-Path $shadowProject 'Builds/AssemblyShadow/M07'
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
$onOutput = Assert-M07NewChild ($(if ($NativeOnOutput) { $NativeOnOutput } else { Join-Path $buildRoot ($BaselineId + '.app') })) $buildRoot 'Native-ON Player output'
$offOutput = Assert-M07NewChild ($(if ($NativeOffOutput) { $NativeOffOutput } else { Join-Path $buildRoot ($BaselineId + '-NativeOff.app') })) $buildRoot 'Native-OFF Player output'
$lockPath = Join-Path $parent 'm07-build.lock'
$workflowLock = [IO.File]::Open($lockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
try {
    if (Test-UnityProjectRunning -ProjectPath $shadowProject) { throw 'This project opened while acquiring the M07 workflow lock.' }
    $common = @('-shadowBaselineId', $BaselineId)
    Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs' $shadowProject $shadowMethods $TimeoutSec $BuildTarget $common
    Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildBaselineResources' $shadowProject $shadowMethods $TimeoutSec $BuildTarget ($common + @('-shadowM07ResourceOutput', $resourceRoot))
    Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildPlayerBaseline' $shadowProject $shadowMethods $TimeoutSec $BuildTarget ($common + @('-shadowBuildOutput', $onOutput))
    Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildFeatureDisabledPlayer' $shadowProject $shadowMethods $TimeoutSec $BuildTarget ($common + @('-shadowBuildOutput', $offOutput))

    Save-M07OriginalSettings $shadowProject $run
    $stageFailure = $null
    $restoreFailure = $null
    try {
        Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07StructuralResources.Prepare' $shadowProject $shadowMethods $TimeoutSec $BuildTarget @('-shadowValidationRoot', $run)
        Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07StructuralResources.Compile' $shadowProject $shadowMethods $TimeoutSec $BuildTarget @('-shadowValidationRoot', $run)
    }
    catch { $stageFailure = $_ }
    finally {
        try {
            Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07StructuralResources.Restore' $shadowProject $shadowMethods $TimeoutSec $BuildTarget @('-shadowValidationRoot', $run)
            Restore-M07OriginalSettingsBytes $shadowProject $run
        }
        catch { $restoreFailure = $_ }
    }
    if ($restoreFailure) { throw "M07 P05 recovery failed. Stage failure: $stageFailure Recovery failure: $restoreFailure" }
    if ($stageFailure) { throw $stageFailure }
    Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07StructuralResources.FinalizeFixtures' $shadowProject $shadowMethods $TimeoutSec $BuildTarget @('-shadowValidationRoot', $run)

    $settingsPath = Join-Path $shadowProject 'ProjectSettings/ProjectSettings.asset'
    $backupPath = Join-Path $run 'p05-project-settings.original'
    if ((Get-M07BytesHash ([IO.File]::ReadAllBytes($settingsPath))) -cne (Get-M07BytesHash ([IO.File]::ReadAllBytes($backupPath)))) {
        throw 'The completed M07 workflow did not preserve the original ProjectSettings bytes.'
    }
    $onReceipt = Find-M07PlayerReceipt $shadowProject 'NativeOn' $onOutput $existingPlayerReceipts
    $offReceipt = Find-M07PlayerReceipt $shadowProject 'NativeOff' $offOutput $existingPlayerReceipts
    $fixtureManifest = Join-Path $run 'm07-fixtures.json'
    $replayReceipt = Join-Path $run 'm07-editor-replay.json'
    foreach ($required in @($onReceipt, $offReceipt, $fixtureManifest, $replayReceipt)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "M07 workflow output is missing: $required" }
    }
    $workflow = [ordered]@{
        schemaVersion = 1; milestone = 'M07'; result = 'Passed'; baselineBuildId = $BaselineId;
        projectPath = $shadowProject; buildTarget = $BuildTarget; runDirectory = $run;
        resourceBaselinePath = $resourceRoot; nativeOnPlayer = $onOutput; nativeOffPlayer = $offOutput;
        nativeOnReceipt = $onReceipt; nativeOffReceipt = $offReceipt;
        fixtureManifest = $fixtureManifest; editorReplayReceipt = $replayReceipt;
        projectSettingsSha256 = Get-M07BytesHash ([IO.File]::ReadAllBytes($settingsPath));
    }
    $workflowPath = Join-Path $run 'm07-build-workflow.json'
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes(($workflow | ConvertTo-Json -Depth 8) + "`n")
    $file = [IO.File]::Open($workflowPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $file.Write($bytes, 0, $bytes.Length); $file.Flush($true) }
    finally { $file.Dispose() }
    Write-Host "M07 build workflow completed: $workflowPath"
    Write-Host "Fixture manifest: $fixtureManifest"
    Write-Host "Native-ON receipt: $onReceipt"
    Write-Host "Native-OFF receipt: $offReceipt"
}
finally { $workflowLock.Dispose() }
