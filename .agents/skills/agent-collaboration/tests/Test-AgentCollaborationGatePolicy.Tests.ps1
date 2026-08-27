$repositoryRoot = $PSScriptRoot
for ($index = 0; $index -lt 4; $index++) {
    $repositoryRoot = Split-Path -Parent $repositoryRoot
}

$profilePath = [System.IO.Path]::Combine($repositoryRoot, ".codex", "agents", "code-gate-reviewer.toml")
$rootSkillPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "agent-collaboration", "SKILL.md")
$clientSkillPath = [System.IO.Path]::Combine($repositoryRoot, "client", ".agents", "skills", "agent-collaboration", "SKILL.md")
$defaultConfigPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "config", "svn.user.default.config.json")
$wangxingConfigPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "config", "svn.user.wangxing.config.json")
$configReadmePath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "config", "README.md")
$rootModeScriptPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "agent-collaboration", "scripts", "Get-GateReviewMode.ps1")
$clientModeScriptPath = [System.IO.Path]::Combine($repositoryRoot, "client", ".agents", "skills", "agent-collaboration", "scripts", "Get-GateReviewMode.ps1")
$fightSkillPaths = @(
    [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "fight-dev-ability", "SKILL.md"),
    [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "fight-dev-breakthrough-passive", "SKILL.md"),
    [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "fight-dev-new-hero", "SKILL.md")
)

Describe "Agent collaboration gate-review contract" {
    It "keeps ordinary gates off by default, forces Fight development by default, and enables all for wangxing" {
        $defaultConfig = Get-Content -LiteralPath $defaultConfigPath -Raw | ConvertFrom-Json
        $wangxingConfig = Get-Content -LiteralPath $wangxingConfigPath -Raw | ConvertFrom-Json

        $defaultConfig.agent_collaboration.require_sol_main_agent_for_gate_review | Should Be $true
        $defaultConfig.agent_collaboration.enable_gate_reviewer | Should Be $false
        $defaultConfig.agent_collaboration.review_committed_major_milestones | Should Be $false
        $defaultConfig.agent_collaboration.require_fight_hero_skill_development_full_gate_review | Should Be $true
        $wangxingConfig.agent_collaboration.require_sol_main_agent_for_gate_review | Should Be $true
        $wangxingConfig.agent_collaboration.enable_gate_reviewer | Should Be $true
        $wangxingConfig.agent_collaboration.review_committed_major_milestones | Should Be $true
        $wangxingConfig.agent_collaboration.require_fight_hero_skill_development_full_gate_review | Should Be $true
        ($defaultConfig.agent_collaboration.PSObject.Properties.Name -contains "require_fight_hero_skill_development_gate_review") | Should Be $false
        ($wangxingConfig.agent_collaboration.PSObject.Properties.Name -contains "require_fight_hero_skill_development_gate_review") | Should Be $false
    }

    It "documents the Fight-only full-gate switch as independent of both ordinary switches" {
        $content = Get-Content -LiteralPath $configReadmePath -Raw

        $content | Should Match ([regex]::Escape("require_fight_hero_skill_development_full_gate_review"))
        $content | Should Match '(?is)require_fight_hero_skill_development_full_gate_review.*优先级高于.*enable_gate_reviewer.*review_committed_major_milestones'
        $content | Should Match '(?is)require_fight_hero_skill_development_full_gate_review.*最终.*里程碑'
        $content | Should Match '(?is)require_fight_hero_skill_development_full_gate_review.*仅.*战斗英雄技能开发.*其他任务'
        $content | Should Not Match ([regex]::Escape("require_fight_hero_skill_development_gate_review"))
    }

    It "documents the Sol main-agent gate prerequisite" {
        $content = Get-Content -LiteralPath $configReadmePath -Raw

        $content | Should Match ([regex]::Escape("require_sol_main_agent_for_gate_review"))
        $content | Should Match '(?is)require_sol_main_agent_for_gate_review.*EffectiveMainAgentModel.*Sol.*enable_gate_reviewer.*review_committed_major_milestones'
        $content | Should Match '(?is)require_sol_main_agent_for_gate_review.*优先于.*战斗英雄技能开发.*完整 Gate Review'
        $content | Should Match '(?is)require_sol_main_agent_for_gate_review.*luna.*terra.*sol'
        $content | Should Match '(?is)宿主实时元数据.*读取一次.*复用'
        $content | Should Match '(?is)EffectiveMainAgentModel.*MainAgentModel.*兼容别名'
        $content | Should Match '(?is)EffectiveMainAgentModel.*完整模型名.*不区分大小写'
        $content | Should Match '(?is)InvalidMainAgentModel.*最多重试一次'
    }

    It "provides a read-only Sol max gate-review profile" {
        $profilePath | Should Exist
        $profile = Get-Content -LiteralPath $profilePath -Raw

        $profile | Should Match '(?m)^name = "code-gate-reviewer"$'
        $profile | Should Match '(?m)^model = "gpt-5\.6-sol"$'
        $profile | Should Match '(?m)^model_reasoning_effort = "max"$'
        $profile | Should Match '(?m)^sandbox_mode = "read-only"$'
    }

    It "does not keep a client-local collaboration policy" {
        $clientSkillPath | Should Not Exist
    }

    It "keeps the canonical compact gate-mode helper" {
        $rootModeScriptPath | Should Exist
        $clientModeScriptPath | Should Not Exist
    }

    foreach ($skillPath in @($rootSkillPath)) {
        It "uses the compact gate-review mode helper in $skillPath" {
            $content = Get-Content -LiteralPath $skillPath -Raw

            $content | Should Match ([regex]::Escape("scripts/Get-GateReviewMode.ps1"))
            $content | Should Match ([regex]::Escape("FinalAndMilestones"))
            $content | Should Match ([regex]::Escape("RequiredFinalAndMilestones"))
            $content | Should Match ([regex]::Escape("FightHeroSkillDevelopment"))
            $content | Should Match ([regex]::Escape("authoritative live host metadata"))
            $content | Should Match '(?is)read.*once.*reuse'
            $content | Should Match ([regex]::Escape("EffectiveMainAgentModel"))
            $content | Should Match '(?is)InvalidMainAgentModel.*retry once'
            $content | Should Match '(?is)require_fight_hero_skill_development_full_gate_review.*higher priority than.*enable_gate_reviewer.*review_committed_major_milestones'
            $content | Should Match '(?is)require_fight_hero_skill_development_full_gate_review.*only.*Fight hero skill development.*never.*other tasks'
            $content | Should Match '(?is)RequiredFinalAndMilestones.*at least one.*milestone.*final gate.*mandatory'
            $content | Should Not Match ([regex]::Escape("require_fight_hero_skill_development_gate_review"))
            $content | Should Not Match ([regex]::Escape("Resolve-SvnUserConfig.ps1"))
            $content | Should Not Match ([regex]::Escape('$enableGateReviewer ='))
        }
    }

    foreach ($fightSkillPath in $fightSkillPaths) {
        It "marks implementation use as FightHeroSkillDevelopment in $fightSkillPath" {
            $content = Get-Content -LiteralPath $fightSkillPath -Raw

            $content | Should Match ([regex]::Escape("FightHeroSkillDevelopment"))
            $content | Should Match '(?is)(?:implement|implementation|develop|development|authoring|execution).*FightHeroSkillDevelopment|FightHeroSkillDevelopment.*(?:implement|implementation|develop|development|authoring|execution)'
            $content | Should Match '(?is)(?:read-only|review|debug).*not.*FightHeroSkillDevelopment|FightHeroSkillDevelopment.*not.*(?:read-only|review|debug)'
        }
    }

    foreach ($skillPath in @($rootSkillPath)) {
        It "requires committed milestone and final gate remediation to be committed before re-review in $skillPath" {
            $content = Get-Content -LiteralPath $skillPath -Raw

            $content | Should Match '(?i)when (?:a|any) gate reviews committed state'
            $content | Should Match '(?i)milestone and final gates'
            $content | Should Match '(?is)FAIL.*BLOCKED.*versioned content'
            $content | Should Match '(?i)expanded (?:cumulative )?immutable revision range'
        }
    }
}

if (Test-Path -LiteralPath $rootModeScriptPath -PathType Leaf) {
    Describe "Get-GateReviewMode" {
        BeforeEach {
            $resolverStubPath = Join-Path $TestDrive "Resolve-SvnUserConfig.ps1"
            @'
[CmdletBinding()]
param(
    [string]$WorkingCopyRoot,
    [string]$SvnExecutable
)

if ($env:TEST_GATE_RESOLVER_THROWS -eq "true") {
    throw "Synthetic resolver failure"
}

$enable = switch ($env:TEST_GATE_ENABLE) {
    "bool:true" { $true }
    "bool:false" { $false }
    default { $env:TEST_GATE_ENABLE }
}
$milestones = switch ($env:TEST_GATE_MILESTONES) {
    "bool:true" { $true }
    "bool:false" { $false }
    default { $env:TEST_GATE_MILESTONES }
}
$fightFullReview = switch ($env:TEST_GATE_FIGHT_FULL_REVIEW) {
    "bool:true" { $true }
    "bool:false" { $false }
    default { $env:TEST_GATE_FIGHT_FULL_REVIEW }
}
$requireSolMainAgent = switch ($env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT) {
    "bool:true" { $true }
    "bool:false" { $false }
    default { $env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT }
}

[pscustomobject]@{
    SvnUser = "wangxing"
    Config = [pscustomobject]@{
        agent_collaboration = [pscustomobject]$(
            $settings = [ordered]@{}
            if ($env:TEST_GATE_ENABLE -ne "missing") {
                $settings.enable_gate_reviewer = $enable
            }
            if ($env:TEST_GATE_MILESTONES -ne "missing") {
                $settings.review_committed_major_milestones = $milestones
            }
            if ($env:TEST_GATE_FIGHT_FULL_REVIEW -ne "missing") {
                $settings.require_fight_hero_skill_development_full_gate_review = $fightFullReview
            }
            if ($env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT -ne "missing") {
                $settings.require_sol_main_agent_for_gate_review = $requireSolMainAgent
            }
            $settings
        )
    }
}
'@ | Set-Content -LiteralPath $resolverStubPath -Encoding UTF8
        }

        AfterEach {
            Remove-Item Env:TEST_GATE_ENABLE -ErrorAction SilentlyContinue
            Remove-Item Env:TEST_GATE_MILESTONES -ErrorAction SilentlyContinue
            Remove-Item Env:TEST_GATE_FIGHT_FULL_REVIEW -ErrorAction SilentlyContinue
            Remove-Item Env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT -ErrorAction SilentlyContinue
            Remove-Item Env:TEST_GATE_RESOLVER_THROWS -ErrorAction SilentlyContinue
        }

        $cases = @(
            @{ Name = "forces both Fight gates when both ordinary switches are false"; Enable = "bool:false"; Milestones = "bool:false"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "RequiredFinalAndMilestones" },
            @{ Name = "forces both Fight gates when the ordinary switches are missing"; Enable = "missing"; Milestones = "missing"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "RequiredFinalAndMilestones" },
            @{ Name = "forces both Fight gates when the ordinary switches are malformed"; Enable = "true"; Milestones = "true"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "RequiredFinalAndMilestones" },
            @{ Name = "forces both Fight gates when only the ordinary master is true"; Enable = "bool:true"; Milestones = "bool:false"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "RequiredFinalAndMilestones" },
            @{ Name = "keeps an ordinary task Off when only the Fight full-gate switch is true"; Enable = "bool:false"; Milestones = "bool:true"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $false; Expected = "Off" },
            @{ Name = "returns Final for an ordinary task regardless of the Fight full-gate switch"; Enable = "bool:true"; Milestones = "bool:false"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $false; Expected = "Final" },
            @{ Name = "returns FinalAndMilestones for an ordinary task regardless of the Fight full-gate switch"; Enable = "bool:true"; Milestones = "bool:true"; FightFullReview = "bool:true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $false; Expected = "FinalAndMilestones" },
            @{ Name = "falls back to Off when the Fight full-gate switch is false"; Enable = "bool:false"; Milestones = "bool:true"; FightFullReview = "bool:false"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "Off" },
            @{ Name = "falls back to Final when the Fight full-gate switch is missing"; Enable = "bool:true"; Milestones = "bool:false"; FightFullReview = "missing"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "Final" },
            @{ Name = "rejects a string Fight full-gate switch"; Enable = "bool:true"; Milestones = "bool:true"; FightFullReview = "true"; RequireSolMainAgent = "missing"; MainAgentModel = ""; FightTask = $true; Expected = "FinalAndMilestones" },
            @{ Name = "returns Off for a mixed-case full Luna model name"; Enable = "bool:true"; Milestones = "bool:true"; FightFullReview = "bool:true"; RequireSolMainAgent = "bool:true"; MainAgentModel = "GPT-5.6-LuNa"; FightTask = $true; Expected = "Off" },
            @{ Name = "returns Off for an uppercase Terra family name"; Enable = "bool:true"; Milestones = "bool:true"; FightFullReview = "bool:true"; RequireSolMainAgent = "bool:true"; MainAgentModel = "TERRA"; FightTask = $true; Expected = "Off" },
            @{ Name = "evaluates both ordinary switches for a title-case full Sol model name"; Enable = "bool:true"; Milestones = "bool:true"; FightFullReview = "bool:false"; RequireSolMainAgent = "bool:true"; MainAgentModel = "GPT-5.6-Sol"; FightTask = $false; Expected = "FinalAndMilestones" },
            @{ Name = "accepts a compact mixed-case Sol model name"; Enable = "bool:true"; Milestones = "bool:false"; FightFullReview = "bool:false"; RequireSolMainAgent = "bool:true"; MainAgentModel = "GPT56sOl"; FightTask = $false; Expected = "Final" },
            @{ Name = "does not apply model-name validation when the Sol restriction is disabled"; Enable = "bool:true"; Milestones = "bool:false"; FightFullReview = "bool:false"; RequireSolMainAgent = "bool:false"; MainAgentModel = "unexpected-model"; FightTask = $false; Expected = "Final" }
        )

        foreach ($case in $cases) {
            It $case.Name {
                $env:TEST_GATE_ENABLE = $case.Enable
                $env:TEST_GATE_MILESTONES = $case.Milestones
                $env:TEST_GATE_FIGHT_FULL_REVIEW = $case.FightFullReview
                $env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT = $case.RequireSolMainAgent

                $parameters = @{
                    WorkingCopyRoot = $TestDrive
                    ResolverPath = $resolverStubPath
                }
                if ($case.FightTask) {
                    $parameters.FightHeroSkillDevelopment = $true
                }
                $parameters.EffectiveMainAgentModel = $case.MainAgentModel
                $mode = & $rootModeScriptPath @parameters

                $mode | Should Be $case.Expected
            }
        }

        foreach ($invalidModel in @("", "inherit", "unexpected-model", "console", "GPT-5.6-Luna-Sol")) {
            It "requires the main agent to re-check invalid model name '$invalidModel'" {
                $env:TEST_GATE_ENABLE = "bool:true"
                $env:TEST_GATE_MILESTONES = "bool:true"
                $env:TEST_GATE_FIGHT_FULL_REVIEW = "bool:true"
                $env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT = "bool:true"

                $caughtError = $null
                try {
                    & $rootModeScriptPath `
                        -WorkingCopyRoot $TestDrive `
                        -ResolverPath $resolverStubPath `
                        -EffectiveMainAgentModel $invalidModel
                }
                catch {
                    $caughtError = $_
                }

                $caughtError | Should Not BeNullOrEmpty
                $caughtError.FullyQualifiedErrorId | Should Match '^InvalidMainAgentModel(?:,|$)'
                $caughtError.Exception.Message | Should Be "Expected exactly one Luna, Terra, or Sol family; verify the effective main-agent model and retry once."
            }
        }

        It "keeps MainAgentModel as a compatibility alias" {
            $env:TEST_GATE_ENABLE = "bool:true"
            $env:TEST_GATE_MILESTONES = "bool:false"
            $env:TEST_GATE_FIGHT_FULL_REVIEW = "bool:false"
            $env:TEST_GATE_REQUIRE_SOL_MAIN_AGENT = "bool:true"

            $mode = & $rootModeScriptPath `
                -WorkingCopyRoot $TestDrive `
                -ResolverPath $resolverStubPath `
                -MainAgentModel "GPT-5.6-Sol"

            $mode | Should Be "Final"
        }

        It "fails safely to Off" {
            $env:TEST_GATE_RESOLVER_THROWS = "true"

            $mode = & $rootModeScriptPath -WorkingCopyRoot $TestDrive -ResolverPath $resolverStubPath

            $mode | Should Be "Off"
        }
    }
}
