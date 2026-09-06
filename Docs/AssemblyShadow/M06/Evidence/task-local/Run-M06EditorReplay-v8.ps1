[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$FixtureManifest,
    [Parameter(Mandatory = $true)][string]$Receipt
)

$ErrorActionPreference = 'Stop'
$project = '/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow'
$invoke = Join-Path $project '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
$manifestPath = [IO.Path]::GetFullPath($FixtureManifest)
$receiptPath = [IO.Path]::GetFullPath($Receipt)
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Fixture manifest is missing: $manifestPath" }
if (Test-Path -LiteralPath $receiptPath) { throw "Replay receipt must be new: $receiptPath" }
$methodArgs = @(
    '-shadowFixtureManifest', $manifestPath,
    '-shadowValidationReceipt', $receiptPath
)

& $invoke `
    -Method 'AssemblyShadowDemo.Editor.M06EditorValidation.Validate' `
    -ProjectPath $project `
    -BuildTarget 'StandaloneOSX' `
    -TimeoutSec 28800 `
    -MethodArgs $methodArgs

exit $LASTEXITCODE
