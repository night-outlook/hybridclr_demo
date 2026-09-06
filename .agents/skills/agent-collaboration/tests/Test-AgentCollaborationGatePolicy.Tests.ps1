$repositoryRoot = $PSScriptRoot
for ($index = 0; $index -lt 4; $index++) {
    $repositoryRoot = Split-Path -Parent $repositoryRoot
}

$rootSkillPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "agent-collaboration", "SKILL.md")
$rootModeScriptPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "skills", "agent-collaboration", "scripts", "Get-GateReviewMode.ps1")
$configPath = [System.IO.Path]::Combine($repositoryRoot, ".agents", "config", "config.json")

Describe "Agent collaboration gate-review contract" {
    It "uses the checked-in repository config" {
        $configPath | Should Exist
        $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
        $config.agent_collaboration.require_sol_or_astra_main_agent_for_gate_review | Should Be $true
        $config.agent_collaboration.enable_gate_reviewer | Should Be $false
        $config.agent_collaboration.review_committed_major_milestones | Should BeOfType ([bool])
    }

    It "keeps the skill Git-native and free of account-specific config lookup" {
        $skillFiles = @($rootSkillPath, $rootModeScriptPath) | ForEach-Object { Get-Item -LiteralPath $_ }
        $content = ($skillFiles | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }) -join "`n"
        $content | Should Not Match ("(?i)" + ("s" + "v" + "n"))
        $accountConfigPattern = "(?i)" + ("u" + "s" + "e" + "r") + ".?name|" + ("R" + "e" + "s" + "o" + "l" + "v" + "e") + ".*" + ("U" + "s" + "e" + "r") + ".*" + ("C" + "o" + "n" + "f" + "i" + "g")
        $content | Should Not Match $accountConfigPattern
    }

    It "documents the direct config path and Git commit terminology" {
        $skillContent = Get-Content -LiteralPath $rootSkillPath -Raw
        $scriptContent = Get-Content -LiteralPath $rootModeScriptPath -Raw
        $skillContent | Should Match '(?i)Git.*commit'
        $scriptContent | Should Match '(?i)Path\]::Combine\(\$repositoryRoot, ".agents", "config", "config\.json"\)'
        $scriptContent | Should Match '(?i)git.*rev-parse'
        $scriptContent | Should Not Match ('(?i)ResolverPath|' + ('s' + 'v' + 'n') + 'Executable|WorkingCopyRoot')
    }
}

if (Test-Path -LiteralPath $rootModeScriptPath -PathType Leaf) {
    Describe "Get-GateReviewMode" {
        BeforeEach {
            $testRepositoryRoot = Join-Path $TestDrive "repository"
            $testConfigDirectory = Join-Path $testRepositoryRoot ".agents\config"
            New-Item -ItemType Directory -Path $testConfigDirectory -Force | Out-Null
        }

        function Set-TestConfig {
            param(
                [bool]$RequireSolOrAstraMainAgent,
                [bool]$EnableGateReviewer,
                [bool]$ReviewMilestones,
                [bool]$FightFullReview
            )

            $testConfig = [ordered]@{
                agent_collaboration = [ordered]@{
                    require_sol_or_astra_main_agent_for_gate_review = $RequireSolOrAstraMainAgent
                    enable_gate_reviewer = $EnableGateReviewer
                    review_committed_major_milestones = $ReviewMilestones
                    require_fight_hero_skill_development_full_gate_review = $FightFullReview
                }
            }
            $testConfig | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $testRepositoryRoot ".agents\config\config.json") -Encoding UTF8
        }

        It "reads gate settings from the repository config" {
            Set-TestConfig -RequireSolOrAstraMainAgent $true -EnableGateReviewer $true -ReviewMilestones $true -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel "GPT-6-Astra"
            $mode | Should Be "FinalAndMilestones"
        }

        It "does not require an account-specific config file" {
            Set-TestConfig -RequireSolOrAstraMainAgent $false -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel "unrecognized-model"
            $mode | Should Be "Final"
        }

        It "allows Sol and Astra family names and full identifiers" {
            Set-TestConfig -RequireSolOrAstraMainAgent $true -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            foreach ($model in @("Sol", "GPT-5.6-SOL", "Astra", "gpt-6-astra", "GPT-6-ASTRA")) {
                (& $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel $model) | Should Be "Final"
            }
        }

        It "excludes other families before the forced Fight gate" {
            Set-TestConfig -RequireSolOrAstraMainAgent $true -EnableGateReviewer $true -ReviewMilestones $true -FightFullReview $true
            foreach ($model in @("gpt-5.6-luna", "gpt-5.6-terra")) {
                (& $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel $model -FightHeroSkillDevelopment) | Should Be "Off"
            }
            (& $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel "gpt-6-astra" -FightHeroSkillDevelopment) | Should Be "RequiredFinalAndMilestones"
        }

        It "rejects missing unknown and ambiguous model identities" {
            Set-TestConfig -RequireSolOrAstraMainAgent $true -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            foreach ($model in @("", "inherit", "gpt-6", "astras", "sol-astra")) {
                { & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel $model } | Should Throw
            }
        }

        It "forces the full Fight gate from the shared config" {
            Set-TestConfig -RequireSolOrAstraMainAgent $false -EnableGateReviewer $false -ReviewMilestones $false -FightFullReview $true
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -FightHeroSkillDevelopment
            $mode | Should Be "RequiredFinalAndMilestones"
        }

        It "returns Off when the direct config is missing or invalid" {
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot
            $mode | Should Be "Off"
            '{ invalid json' | Set-Content -LiteralPath (Join-Path $testRepositoryRoot ".agents\config\config.json") -Encoding UTF8
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot
            $mode | Should Be "Off"
        }

        It "keeps MainAgentModel as a compatibility alias" {
            Set-TestConfig -RequireSolOrAstraMainAgent $true -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -MainAgentModel "GPT-6-Astra"
            $mode | Should Be "Final"
        }
    }
}
