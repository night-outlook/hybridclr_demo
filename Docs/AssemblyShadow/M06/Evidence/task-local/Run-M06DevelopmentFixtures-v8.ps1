$ErrorActionPreference = 'Stop'

$project = '/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow'
$invoke = Join-Path $project '.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1'
$generation = Join-Path $project '_temp/AssemblyShadow/M06Generation-121a2a74c5f844b2b09b0f3e49e24eef/m06-generation.json'
$methodArgs = @(
    '-shadowBaselineId', 'M06-Baseline-v8',
    '-shadowM06BuildMode', 'Development',
    '-shadowM06Generation', $generation
)

& $invoke `
    -Method 'AssemblyShadowDemo.Editor.M06Build.BuildFixtures' `
    -ProjectPath $project `
    -BuildTarget 'StandaloneOSX' `
    -TimeoutSec 28800 `
    -MethodArgs $methodArgs

exit $LASTEXITCODE
