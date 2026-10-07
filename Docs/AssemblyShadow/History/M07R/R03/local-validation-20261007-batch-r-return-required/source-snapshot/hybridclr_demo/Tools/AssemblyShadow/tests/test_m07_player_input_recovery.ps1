param(
    [string]$CorePath = (Join-Path $PSScriptRoot '../Invoke-M07Build.Core.ps1')
)

$ErrorActionPreference = 'Stop'
$core = [IO.Path]::GetFullPath($CorePath)
if (-not (Test-Path -LiteralPath $core -PathType Leaf)) { throw "M07 core script is missing: $core" }

$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($core, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0) { throw "M07 core PowerShell parse failed: $($parseErrors[0].Message)" }

foreach ($name in @('Get-M07BytesHash', 'Assert-M07RegularPath', 'Invoke-M07PlayerMethodWithGeneratedInputRecovery')) {
    $function = $ast.Find({
        param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -ceq $name
    }, $true)
    if ($null -eq $function) { throw "$name was not found in the M07 core." }
    Invoke-Expression $function.Extent.Text
}

function Test-UnityProjectRunning { param([string]$ProjectPath); return $false }

$script:ThrowAfterMutation = $false
function Invoke-M07GuardedMethod {
    param([string]$Method, [string]$Project, [string]$MethodScript, [int]$Timeout, [string]$Target, [string[]]$Arguments)
    [IO.File]::WriteAllText((Join-Path $Project 'Assets/HybridCLRGenerate/link.xml'), '<linker><assembly fullname="generated"/></linker>')
    [IO.File]::WriteAllText((Join-Path $Project 'ProjectSettings/ProjectSettings.asset'), 'il2cppCodeGeneration:' + [Environment]::NewLine + '  Standalone: 0' + [Environment]::NewLine)
    if ($script:ThrowAfterMutation) { throw 'M07_RECOVERY_STAGE_FAILURE' }
}

function Invoke-RecoveryCase {
    param([bool]$FailStage)
    $root = Join-Path ([IO.Path]::GetTempPath()) ('m07-player-input-recovery-' + [guid]::NewGuid().ToString('N'))
    $project = Join-Path $root 'project'
    $run = Join-Path $root 'run'
    New-Item -ItemType Directory -Path (Join-Path $project 'Assets/HybridCLRGenerate') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $project 'ProjectSettings') -Force | Out-Null
    New-Item -ItemType Directory -Path $run -Force | Out-Null
    $link = Join-Path $project 'Assets/HybridCLRGenerate/link.xml'
    $settings = Join-Path $project 'ProjectSettings/ProjectSettings.asset'
    $linkOriginal = [Text.UTF8Encoding]::new($false).GetBytes('<linker/>')
    $settingsOriginal = [Text.UTF8Encoding]::new($false).GetBytes('il2cppCodeGeneration: {}' + [Environment]::NewLine)
    [IO.File]::WriteAllBytes($link, $linkOriginal)
    [IO.File]::WriteAllBytes($settings, $settingsOriginal)

    $script:ThrowAfterMutation = $FailStage
    $caught = $null
    try {
        $invoke = @{ Method='RecoveryProbe'; Project=$project; MethodScript='/tmp/unused.ps1'; Timeout=1; Target='StandaloneOSX'; Arguments=@(); Run=$run; Label='native-on-controlled' }
        Invoke-M07PlayerMethodWithGeneratedInputRecovery @invoke
    }
    catch { $caught = $_ }

    try {
        if ((Get-M07BytesHash ([IO.File]::ReadAllBytes($link))) -cne (Get-M07BytesHash $linkOriginal)) { throw 'link.xml exact-byte restoration failed.' }
        if ((Get-M07BytesHash ([IO.File]::ReadAllBytes($settings))) -cne (Get-M07BytesHash $settingsOriginal)) { throw 'ProjectSettings.asset exact-byte restoration failed.' }
        foreach ($key in @('link-xml', 'project-settings')) {
            $receiptPath = Join-Path $run ('native-on-controlled-' + $key + '-restored.json')
            if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) { throw "Missing restoration receipt: $receiptPath" }
            $receipt = Get-Content -Raw -LiteralPath $receiptPath | ConvertFrom-Json
            if ($receipt.status -cne 'ExactBytesRestored' -or -not $receipt.changed -or $receipt.originalSha256 -cne $receipt.restoredSha256) { throw "Invalid restoration receipt for $key" }
        }
        if ($FailStage) {
            if ($null -eq $caught -or $caught.Exception.Message -cne 'M07_RECOVERY_STAGE_FAILURE') { throw "Original stage failure was not preserved after exact-byte recovery: $caught" }
        }
        elseif ($null -ne $caught) { throw "Successful recovery case unexpectedly failed: $caught" }
    }
    finally { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}

Invoke-RecoveryCase -FailStage $false
Invoke-RecoveryCase -FailStage $true

[ordered]@{
    schemaVersion = 1
    kind = 'M07PlayerMutableInputRecoveryTest'
    result = 'Passed'
    inputs = @('Assets/HybridCLRGenerate/link.xml', 'ProjectSettings/ProjectSettings.asset')
    successPath = 'Passed'
    failurePath = 'PassedAndOriginalFailurePreserved'
    unityInvoked = $false
} | ConvertTo-Json -Depth 4
