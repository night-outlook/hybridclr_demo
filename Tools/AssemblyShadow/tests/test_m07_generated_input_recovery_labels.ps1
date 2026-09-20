param(
    [string]$CorePath = (Join-Path $PSScriptRoot '../Invoke-M07Build.Core.ps1')
)

$ErrorActionPreference = 'Stop'
$core = [IO.Path]::GetFullPath($CorePath)
if (-not (Test-Path -LiteralPath $core -PathType Leaf)) {
    throw "M07 core script is missing: $core"
}

$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $core,
    [ref]$tokens,
    [ref]$parseErrors)
if ($parseErrors.Count -ne 0) {
    throw "M07 core PowerShell parse failed: $($parseErrors[0].Message)"
}

$function = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -ceq 'Invoke-M07PlayerMethodWithGeneratedInputRecovery'
}, $true)
if ($null -eq $function) {
    throw 'Invoke-M07PlayerMethodWithGeneratedInputRecovery was not found in the M07 core.'
}

# Load the actual production function definition without executing the workflow.
Invoke-Expression $function.Extent.Text

# The helper's first Unity-dependent operation is Test-UnityProjectRunning.
# Throwing a sentinel here proves PowerShell parameter binding accepted the
# supplied Label and entered the actual helper body before any Unity work.
function Test-UnityProjectRunning {
    param([string]$ProjectPath)
    throw [InvalidOperationException]::new('M07_RECOVERY_BINDER_BODY_ENTERED')
}

function Assert-M07AcceptedRecoveryLabel {
    param([string]$Label)
    try {
        Invoke-M07PlayerMethodWithGeneratedInputRecovery \
            -Method 'BinderProbe' \
            -Project '/tmp/m07-binder-probe' \
            -MethodScript '/tmp/unused.ps1' \
            -Timeout 1 \
            -Target 'StandaloneOSX' \
            -Arguments @() \
            -Run '/tmp/m07-binder-probe-run' \
            -Label $Label
        throw "Accepted label '$Label' did not reach the binder-body sentinel."
    }
    catch {
        if ($_.Exception.Message -cne 'M07_RECOVERY_BINDER_BODY_ENTERED') {
            throw "Label '$Label' failed before helper-body entry: $($_.Exception.GetType().FullName): $($_.Exception.Message)"
        }
    }
}

foreach ($label in @('native-on', 'native-off', 'native-on-controlled', 'native-off-controlled')) {
    Assert-M07AcceptedRecoveryLabel -Label $label
}

$invalidRejected = $false
try {
    Invoke-M07PlayerMethodWithGeneratedInputRecovery \
        -Method 'BinderProbe' \
        -Project '/tmp/m07-binder-probe' \
        -MethodScript '/tmp/unused.ps1' \
        -Timeout 1 \
        -Target 'StandaloneOSX' \
        -Arguments @() \
        -Run '/tmp/m07-binder-probe-run' \
        -Label 'native-on-unknown'
}
catch {
    if ($_.Exception.Message -ceq 'M07_RECOVERY_BINDER_BODY_ENTERED') {
        throw 'Unknown recovery label entered the helper body.'
    }
    if ($_.Exception -is [System.Management.Automation.ParameterBindingValidationException] -or
        $_.Exception.Message -match 'ValidateSet') {
        $invalidRejected = $true
    }
    else {
        throw "Unknown recovery label failed for an unexpected reason: $($_.Exception.GetType().FullName): $($_.Exception.Message)"
    }
}
if (-not $invalidRejected) {
    throw 'Unknown recovery label was not rejected by the production parameter binder.'
}

[ordered]@{
    schemaVersion = 1
    kind = 'M07GeneratedInputRecoveryLabelBinderTest'
    result = 'Passed'
    acceptedLabels = @('native-on', 'native-off', 'native-on-controlled', 'native-off-controlled')
    invalidLabelRejected = $true
    unityInvoked = $false
} | ConvertTo-Json -Depth 4
