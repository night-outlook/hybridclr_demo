[CmdletBinding(DefaultParameterSetName = "Json")]
param(
    [Parameter(Mandatory = $true, ParameterSetName = "Json")]
    [string]$StateJson,

    [Parameter(Mandatory = $true, ParameterSetName = "Path")]
    [string]$StatePath,

    [switch]$AsJson
)

function Write-ReadinessResult {
    param(
        [bool]$Ready,
        [string[]]$BlockingReasons,
        [AllowNull()]
        [object]$ObservedAtUnixMs,
        [AllowNull()]
        [object]$ObservedAgeMs,
        [int]$ExitCode
    )

    $result = [ordered]@{
        ready = $Ready
        blockingReasons = @($BlockingReasons)
        observedAtUnixMs = $ObservedAtUnixMs
        observedAgeMs = $ObservedAgeMs
    }

    if ($AsJson) {
        $result | ConvertTo-Json -Compress
    }
    elseif ($Ready) {
        "ready"
    }
    else {
        "blocked: " + ($BlockingReasons -join ",")
    }

    exit $ExitCode
}

function Get-RequiredValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Root,
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $current = $Root
    foreach ($segment in $Path.Split(".")) {
        if ($null -eq $current) {
            throw "Missing required state field."
        }

        $property = $current.PSObject.Properties[$segment]
        if ($null -eq $property) {
            throw "Missing required state field."
        }
        $current = $property.Value
    }
    Write-Output -NoEnumerate -InputObject $current
}

function Get-RequiredBoolean {
    param([object]$Root, [string]$Path)

    $value = Get-RequiredValue -Root $Root -Path $Path
    if ($value -isnot [bool]) {
        throw "Required state field has the wrong type."
    }
    return $value
}

function Get-RequiredIntegral {
    param([object]$Root, [string]$Path)

    $value = Get-RequiredValue -Root $Root -Path $Path
    $integralTypes = @(
        [byte], [sbyte], [short], [ushort], [int], [uint], [long], [ulong]
    )
    if (-not ($integralTypes -contains $value.GetType())) {
        throw "Required state field has the wrong type."
    }
    return [long]$value
}

try {
    if ($PSCmdlet.ParameterSetName -eq "Path") {
        $StateJson = Get-Content -LiteralPath $StatePath -Raw -ErrorAction Stop
    }

    $state = $StateJson | ConvertFrom-Json -ErrorAction Stop
    if ($null -eq $state -or $state -is [System.Array]) {
        throw "State must be a JSON object."
    }

    [long]$observedAtUnixMs = Get-RequiredIntegral $state "observed_at_unix_ms"
    [long]$observedAgeMs = Get-RequiredIntegral $state "staleness.age_ms"
    if ($observedAgeMs -lt 0) {
        throw "Required state field is outside its valid range."
    }

    $readyForTools = Get-RequiredBoolean $state "advice.ready_for_tools"
    $adviceBlockers = Get-RequiredValue $state "advice.blocking_reasons"
    if ($adviceBlockers -isnot [System.Array]) {
        throw "Required state field has the wrong type."
    }
    foreach ($blocker in $adviceBlockers) {
        if ($blocker -isnot [string]) {
            throw "Required state field has the wrong type."
        }
    }
    $activityPhase = Get-RequiredValue $state "activity.phase"
    if ($activityPhase -isnot [string] -or [string]::IsNullOrWhiteSpace($activityPhase)) {
        throw "Required state field has the wrong type."
    }
    $isPlaying = Get-RequiredBoolean $state "editor.play_mode.is_playing"
    $isPaused = Get-RequiredBoolean $state "editor.play_mode.is_paused"
    $isChanging = Get-RequiredBoolean $state "editor.play_mode.is_changing"
    $isCompiling = Get-RequiredBoolean $state "compilation.is_compiling"
    $isDomainReloadPending = Get-RequiredBoolean $state "compilation.is_domain_reload_pending"
    $isUpdating = Get-RequiredBoolean $state "assets.is_updating"
    $externalChangesDirty = Get-RequiredBoolean $state "assets.external_changes_dirty"
    $refreshInProgress = Get-RequiredBoolean $state "assets.refresh.is_refresh_in_progress"
    $testsRunning = Get-RequiredBoolean $state "tests.is_running"
    $stateIsStale = Get-RequiredBoolean $state "staleness.is_stale"
}
catch {
    Write-ReadinessResult -Ready $false -BlockingReasons @("malformed_state") -ObservedAtUnixMs $null -ObservedAgeMs $null -ExitCode 1
}

$reasons = [System.Collections.Generic.List[string]]::new()
if (-not $readyForTools) { $reasons.Add("not_ready_for_tools") }
if ($adviceBlockers.Count -gt 0) { $reasons.Add("advice_blocked") }
if ($activityPhase -cne "idle") { $reasons.Add("activity_not_idle") }
if ($isPlaying -or $isPaused -or $isChanging) { $reasons.Add("play_mode_active") }
if ($isCompiling) { $reasons.Add("compiling") }
if ($isDomainReloadPending) { $reasons.Add("domain_reload_pending") }
if ($isUpdating) { $reasons.Add("assets_updating") }
if ($externalChangesDirty) { $reasons.Add("external_changes_dirty") }
if ($refreshInProgress) { $reasons.Add("refresh_in_progress") }
if ($testsRunning) { $reasons.Add("tests_running") }
if ($stateIsStale) { $reasons.Add("state_stale") }

if ($reasons.Count -gt 0) {
    Write-ReadinessResult -Ready $false -BlockingReasons $reasons.ToArray() -ObservedAtUnixMs $observedAtUnixMs -ObservedAgeMs $observedAgeMs -ExitCode 2
}

Write-ReadinessResult -Ready $true -BlockingReasons @() -ObservedAtUnixMs $observedAtUnixMs -ObservedAgeMs $observedAgeMs -ExitCode 0
