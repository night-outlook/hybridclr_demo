$ErrorActionPreference = 'Stop'

$project = '/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow'
$invoke = Join-Path $project '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
$methodArgs = @(
    '-shadowBaselineId', 'M06-Baseline-Release-v8',
    '-shadowM06BuildMode', 'Release'
)

& $invoke `
    -Method 'AssemblyShadowDemo.Editor.M06Build.PrepareGenerationInputs' `
    -ProjectPath $project `
    -BuildTarget 'StandaloneOSX' `
    -TimeoutSec 28800 `
    -MethodArgs $methodArgs

exit $LASTEXITCODE
