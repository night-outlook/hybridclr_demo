$scriptPath = Join-Path $PSScriptRoot "..\scripts\Test-UnityPlayReadiness.ps1"
$fixtureRoot = Join-Path $PSScriptRoot "fixtures"
$powershellPath = (Get-Process -Id $PID).Path

function Invoke-ReadinessChecker {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FixtureName
    )

    $fixturePath = Join-Path $fixtureRoot $FixtureName
    $output = & $powershellPath -NoProfile -NonInteractive -File $scriptPath -StatePath $fixturePath -AsJson 2>&1
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Output = ($output | Out-String).Trim()
    }
}

Describe "Test-UnityPlayReadiness" {
    It "accepts one complete non-stale idle snapshot" {
        $result = Invoke-ReadinessChecker "editor-state-ready.json"
        $payload = $result.Output | ConvertFrom-Json

        $result.ExitCode | Should Be 0
        $payload.ready | Should Be $true
        @($payload.blockingReasons).Count | Should Be 0
        $payload.observedAtUnixMs | Should Be 1783915200000
        $payload.observedAgeMs | Should Be 100
        ($payload.PSObject.Properties.Name -contains "maxStateAgeMs") | Should Be $false
    }

    $blockedCases = @(
        @{ Fixture = "editor-state-not-ready-for-tools.json"; Reasons = @("not_ready_for_tools") },
        @{ Fixture = "editor-state-activity.json"; Reasons = @("activity_not_idle") },
        @{ Fixture = "editor-state-uppercase-idle.json"; Reasons = @("activity_not_idle") },
        @{ Fixture = "editor-state-playing.json"; Reasons = @("play_mode_active") },
        @{ Fixture = "editor-state-paused.json"; Reasons = @("play_mode_active") },
        @{ Fixture = "editor-state-changing.json"; Reasons = @("play_mode_active") },
        @{ Fixture = "editor-state-compiling.json"; Reasons = @("compiling") },
        @{ Fixture = "editor-state-domain-reload-pending.json"; Reasons = @("domain_reload_pending") },
        @{ Fixture = "editor-state-assets-updating.json"; Reasons = @("assets_updating") },
        @{ Fixture = "editor-state-external-changes-dirty.json"; Reasons = @("external_changes_dirty") },
        @{ Fixture = "editor-state-tests-running.json"; Reasons = @("tests_running") },
        @{ Fixture = "editor-state-transport-stale-accepted.json"; Reasons = @("not_ready_for_tools", "advice_blocked", "state_stale") },
        @{ Fixture = "editor-state-stale.json"; Reasons = @("not_ready_for_tools", "advice_blocked", "state_stale") },
        @{ Fixture = "editor-state-stale-extra-blocker.json"; Reasons = @("not_ready_for_tools", "advice_blocked", "state_stale") },
        @{ Fixture = "editor-state-ready-with-blocker.json"; Reasons = @("advice_blocked") },
        @{ Fixture = "editor-state-refresh-in-progress.json"; Reasons = @("refresh_in_progress") }
    )

    foreach ($case in $blockedCases) {
        It "blocks $($case.Fixture) with only its deterministic reasons" {
            $result = Invoke-ReadinessChecker $case.Fixture
            $payload = $result.Output | ConvertFrom-Json

            $result.ExitCode | Should Be 2
            $payload.ready | Should Be $false
            (@($payload.blockingReasons) -join ",") | Should Be ($case.Reasons -join ",")
        }
    }

    It "returns malformed for invalid JSON" {
        $result = Invoke-ReadinessChecker "editor-state-malformed.json"
        $payload = $result.Output | ConvertFrom-Json

        $result.ExitCode | Should Be 1
        $payload.ready | Should Be $false
        (@($payload.blockingReasons) -contains "malformed_state") | Should Be $true
    }

    It "returns malformed when an exact required field is missing" {
        $result = Invoke-ReadinessChecker "editor-state-missing-field.json"
        $payload = $result.Output | ConvertFrom-Json

        $result.ExitCode | Should Be 1
        (@($payload.blockingReasons) -contains "malformed_state") | Should Be $true
    }

    $wrongTypeCases = @(
        "editor-state-missing-observed.json",
        "editor-state-string-timestamp.json",
        "editor-state-wrong-boolean-string.json",
        "editor-state-wrong-boolean-number.json",
        "editor-state-malformed-age-string.json",
        "editor-state-malformed-blockers-string.json",
        "editor-state-malformed-blocker-item.json"
    )

    foreach ($fixture in $wrongTypeCases) {
        It "fails closed for malformed contract fixture $fixture" {
            $result = Invoke-ReadinessChecker $fixture
            $payload = $result.Output | ConvertFrom-Json

            $result.ExitCode | Should Be 1
            $payload.ready | Should Be $false
            (@($payload.blockingReasons) -join ",") | Should Be "malformed_state"
        }
    }

    It "accepts raw state JSON through StateJson" {
        $stateJson = Get-Content -Raw (Join-Path $fixtureRoot "editor-state-ready.json")
        $output = & $powershellPath -NoProfile -NonInteractive -File $scriptPath -StateJson $stateJson -AsJson 2>&1
        $payload = ($output | Out-String) | ConvertFrom-Json

        $LASTEXITCODE | Should Be 0
        $payload.ready | Should Be $true
    }
}
