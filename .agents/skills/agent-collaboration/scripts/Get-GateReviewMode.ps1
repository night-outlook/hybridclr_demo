[CmdletBinding()]
param(
    [string]$WorkingCopyRoot,
    [string]$SvnExecutable,
    [string]$ResolverPath,
    [Alias("MainAgentModel")]
    [string]$EffectiveMainAgentModel,
    [switch]$FightHeroSkillDevelopment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Find-SvnUserConfigResolver {
    param([Parameter(Mandatory = $true)][string]$StartPath)

    $directory = [System.IO.DirectoryInfo][System.IO.Path]::GetFullPath($StartPath)
    while ($null -ne $directory) {
        $candidate = [System.IO.Path]::Combine(
            $directory.FullName,
            ".agents",
            "scripts",
            "Resolve-SvnUserConfig.ps1"
        )
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
        $directory = $directory.Parent
    }

    throw "Cannot find the shared SVN user config resolver."
}

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

function Get-ValidatedMainAgentModelFamily {
    param([AllowNull()][object]$Model)

    $matchedFamilies = @()
    if ($Model -is [string] -and -not [string]::IsNullOrWhiteSpace($Model)) {
        $matchedFamilies = @(
            [regex]::Matches($Model, "(?i)(?<![a-z])(luna|terra|sol)(?![a-z])") |
                ForEach-Object { $_.Groups[1].Value.ToLowerInvariant() } |
                Select-Object -Unique
        )
    }

    if ($matchedFamilies.Count -ne 1) {
        Write-Error -Message "Expected exactly one Luna, Terra, or Sol family; verify the effective main-agent model and retry once." -ErrorId "InvalidMainAgentModel" -Category InvalidArgument -TargetObject $Model -ErrorAction Stop
    }

    return $matchedFamilies[0]
}

try {
    if ([string]::IsNullOrWhiteSpace($ResolverPath)) {
        $searchRoot = if ([string]::IsNullOrWhiteSpace($WorkingCopyRoot)) {
            (Get-Location).Path
        }
        else {
            $WorkingCopyRoot
        }
        $ResolverPath = Find-SvnUserConfigResolver -StartPath $searchRoot
    }

    $resolverParameters = @{}
    if (-not [string]::IsNullOrWhiteSpace($WorkingCopyRoot)) {
        $resolverParameters.WorkingCopyRoot = $WorkingCopyRoot
    }
    if (-not [string]::IsNullOrWhiteSpace($SvnExecutable)) {
        $resolverParameters.SvnExecutable = $SvnExecutable
    }

    $resolved = & $ResolverPath @resolverParameters -WarningAction SilentlyContinue
    $rootConfig = Get-OptionalPropertyValue -Object $resolved -Name "Config"
    $config = Get-OptionalPropertyValue -Object $rootConfig -Name "agent_collaboration"
    $requireSolMainAgent = Get-OptionalPropertyValue -Object $config -Name "require_sol_main_agent_for_gate_review"
}
catch {
    return "Off"
}

if ($requireSolMainAgent -is [bool] -and $requireSolMainAgent) {
    $mainAgentModelFamily = Get-ValidatedMainAgentModelFamily -Model $EffectiveMainAgentModel
    if ($mainAgentModelFamily -ne "sol") {
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
