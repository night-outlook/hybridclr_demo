[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$Generation)

$ErrorActionPreference = 'Stop'
$project = '/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow'
$invoke = Join-Path $project '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
$generationPath = [IO.Path]::GetFullPath($Generation)
if (-not (Test-Path -LiteralPath $generationPath -PathType Leaf)) { throw "Release generation proof is missing: $generationPath" }
$methodArgs = @(
    '-shadowBaselineId', 'M06-Baseline-Release-v8',
    '-shadowM06BuildMode', 'Release',
    '-shadowM06Generation', $generationPath
)

& $invoke `
    -Method 'AssemblyShadowDemo.Editor.M06Build.BuildReleasePlayerBaseline' `
    -ProjectPath $project `
    -BuildTarget 'StandaloneOSX' `
    -TimeoutSec 28800 `
    -MethodArgs $methodArgs

exit $LASTEXITCODE
