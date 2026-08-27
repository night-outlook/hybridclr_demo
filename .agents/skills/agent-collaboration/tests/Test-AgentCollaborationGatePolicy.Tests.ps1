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
        $config.agent_collaboration.require_sol_main_agent_for_gate_review | Should Be $true
        $config.agent_collaboration.enable_gate_reviewer | Should Be $false
        $config.agent_collaboration.review_committed_major_milestones | Should Be $false
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
                [bool]$RequireSolMainAgent,
                [bool]$EnableGateReviewer,
                [bool]$ReviewMilestones,
                [bool]$FightFullReview
            )

            $testConfig = [ordered]@{
                agent_collaboration = [ordered]@{
                    require_sol_main_agent_for_gate_review = $RequireSolMainAgent
                    enable_gate_reviewer = $EnableGateReviewer
                    review_committed_major_milestones = $ReviewMilestones
                    require_fight_hero_skill_development_full_gate_review = $FightFullReview
                }
            }
            $testConfig | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $testRepositoryRoot ".agents\config\config.json") -Encoding UTF8
        }

        It "reads gate settings from the repository config" {
            Set-TestConfig -RequireSolMainAgent $true -EnableGateReviewer $true -ReviewMilestones $true -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel "GPT-5.6-Sol"
            $mode | Should Be "FinalAndMilestones"
        }

        It "does not require an account-specific config file" {
            Set-TestConfig -RequireSolMainAgent $false -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -EffectiveMainAgentModel "unrecognized-model"
            $mode | Should Be "Final"
        }

        It "forces the full Fight gate from the shared config" {
            Set-TestConfig -RequireSolMainAgent $false -EnableGateReviewer $false -ReviewMilestones $false -FightFullReview $true
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
            Set-TestConfig -RequireSolMainAgent $true -EnableGateReviewer $true -ReviewMilestones $false -FightFullReview $false
            $mode = & $rootModeScriptPath -RepositoryRoot $testRepositoryRoot -MainAgentModel "GPT-5.6-Sol"
            $mode | Should Be "Final"
        }
    }
}
