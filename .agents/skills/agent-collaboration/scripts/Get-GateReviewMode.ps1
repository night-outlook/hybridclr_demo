[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [Alias("MainAgentModel")]
    [string]$EffectiveMainAgentModel,
    [switch]$FightHeroSkillDevelopment,
    [switch]$ReviewerModel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-OptionalPropertyValue {
    param(
        [AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function Get-GitRepositoryRoot {
    param([Parameter(Mandatory = $true)][string]$StartPath)

    $resolvedStartPath = [System.IO.Path]::GetFullPath($StartPath)
    $gitRoot = (& git -C $resolvedStartPath rev-parse --show-toplevel 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitRoot)) {
        return $gitRoot.Trim()
    }

    return $resolvedStartPath
}

function Get-ValidatedMainAgentModelFamily {
    param([AllowNull()][object]$Model)

    $matchedFamilies = @()
    if ($Model -is [string] -and -not [string]::IsNullOrWhiteSpace($Model)) {
        $matchedFamilies = @(
            [regex]::Matches($Model, "(?i)(?<![a-z])(luna|terra|sol|astra)(?![a-z])") |
                ForEach-Object { $_.Groups[1].Value.ToLowerInvariant() } |
                Select-Object -Unique
        )
    }

    if ($matchedFamilies.Count -ne 1) {
        Write-Error -Message "Expected exactly one Luna, Terra, Sol, or Astra family; verify the effective main-agent model and retry once." -ErrorId "InvalidMainAgentModel" -Category InvalidArgument -TargetObject $Model -ErrorAction Stop
    }

    return $matchedFamilies[0]
}

# Resolve only after a non-Off gate mode. This query never changes gate enablement.
if ($ReviewerModel) {
    $family = Get-ValidatedMainAgentModelFamily -Model $EffectiveMainAgentModel
    if ($family -eq "sol") { return "gpt-5.6-sol" }
    # Preserve the Astra default for Luna/Terra when the family restriction is off.
    return "gpt-6-astra"
}

try {
    $startPath = if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
        (Get-Location).Path
    }
    else {
        $RepositoryRoot
    }
    $repositoryRoot = Get-GitRepositoryRoot -StartPath $startPath
    $configPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "config", "config.json")
    $rootConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
    $config = Get-OptionalPropertyValue -Object $rootConfig -Name "agent_collaboration"
    $requireSolOrAstraMainAgent = Get-OptionalPropertyValue -Object $config -Name "require_sol_or_astra_main_agent_for_gate_review"
    # The new key wins by presence, including explicit false.
    if ($null -ne $config -and $null -eq $config.PSObject.Properties["require_sol_or_astra_main_agent_for_gate_review"]) {
        $requireSolOrAstraMainAgent = Get-OptionalPropertyValue -Object $config -Name "require_astra_main_agent_for_gate_review"
    }
}
catch {
    return "Off"
}

if ($requireSolOrAstraMainAgent -is [bool] -and $requireSolOrAstraMainAgent) {
    $mainAgentModelFamily = Get-ValidatedMainAgentModelFamily -Model $EffectiveMainAgentModel
    if ($mainAgentModelFamily -notin @("sol", "astra")) {
        return "Off"
    }
}

try {
    if ($FightHeroSkillDevelopment) {
        $fightFullReview = Get-OptionalPropertyValue -Object $config -Name "require_fight_hero_skill_development_full_gate_review"
        if ($fightFullReview -is [bool] -and $fightFullReview) {
            return "RequiredFinalAndMilestones"
        }
    }

    $enabled = Get-OptionalPropertyValue -Object $config -Name "enable_gate_reviewer"
    if ($enabled -isnot [bool] -or -not $enabled) {
        return "Off"
    }
    $milestones = Get-OptionalPropertyValue -Object $config -Name "review_committed_major_milestones"
    if ($milestones -is [bool] -and $milestones) {
        return "FinalAndMilestones"
    }
    return "Final"
}
catch {
    return "Off"
}
