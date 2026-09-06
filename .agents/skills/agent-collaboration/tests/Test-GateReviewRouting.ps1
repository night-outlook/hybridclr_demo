# Standalone regression matrix; no Pester dependency. Only writes its temporary fixture.
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot '../scripts/Get-GateReviewMode.ps1'
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path (Join-Path $tempRoot '.agents/config') -Force | Out-Null
$count = 0
function Assert-Equal($actual, $expected, $label) {
    if ($actual -ne $expected) { throw "$label expected $expected, got $actual" }
}
function Save-Config($settings) {
    @{agent_collaboration=$settings} | ConvertTo-Json | Set-Content (Join-Path $tempRoot '.agents/config/config.json')
}
try {
    foreach ($restricted in @($false,$true)) {
        foreach ($enabled in @($false,$true)) {
            foreach ($milestones in @($false,$true)) {
                foreach ($fight in @($false,$true)) {
                    foreach ($invokeFight in @($false,$true)) {
                        Save-Config @{require_sol_or_astra_main_agent_for_gate_review=$restricted; enable_gate_reviewer=$enabled; review_committed_major_milestones=$milestones; require_fight_hero_skill_development_full_gate_review=$fight}
                        foreach ($model in @('Sol','GPT-5.6-SOL','Astra','gpt-6-astra','GPT-6-ASTRA','gpt-5.6-luna','gpt-5.6-terra','','inherit','gpt-6','sol-astra')) {
                            $invalid = $model -in @('','inherit','gpt-6','sol-astra')
                            if ($restricted -and $invalid) {
                                $caught = $false
                                try { & $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel $model -FightHeroSkillDevelopment:$invokeFight | Out-Null }
                                catch { if ($_.FullyQualifiedErrorId -notlike 'InvalidMainAgentModel*') { throw }; $caught=$true }
                                if (!$caught) { throw "Expected invalid identity: $model" }
                            } else {
                                $expected = if ($restricted -and $model -in @('gpt-5.6-luna','gpt-5.6-terra')) {'Off'} elseif ($invokeFight -and $fight) {'RequiredFinalAndMilestones'} elseif (!$enabled) {'Off'} elseif ($milestones) {'FinalAndMilestones'} else {'Final'}
                                Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -MainAgentModel $model -FightHeroSkillDevelopment:$invokeFight) $expected "Mode for $model"
                            }
                            $count++
                        }
                    }
                }
            }
        }
    }
    foreach ($model in @('Sol','gpt-5.6-sol','GPT-5.6-SOL','Astra','gpt-6-astra','gpt-5.6-luna','gpt-5.6-terra')) {
        $expected = if ($model -match '(?i)sol') {'gpt-5.6-sol'} else {'gpt-6-astra'}
        Assert-Equal (& $scriptPath -ReviewerModel -MainAgentModel $model) $expected 'Reviewer model'
        $count++
    }
    foreach ($model in @('','inherit','sol-astra','astras')) {
        $caught = $false
        try { & $scriptPath -ReviewerModel -EffectiveMainAgentModel $model | Out-Null }
        catch { if ($_.FullyQualifiedErrorId -notlike 'InvalidMainAgentModel*') { throw }; $caught=$true }
        if (!$caught) { throw "Reviewer query accepted invalid identity: $model" }
        $count++
    }
    Save-Config @{require_astra_main_agent_for_gate_review=$true;enable_gate_reviewer=$true}
    foreach ($model in @('sol','astra','luna','terra')) {
        $expected = if ($model -in @('sol','astra')) {'Final'} else {'Off'}
        Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel $model) $expected 'Legacy option'
        $count++
    }
    foreach ($newValue in @($false,$true)) {
        Save-Config @{require_sol_or_astra_main_agent_for_gate_review=$newValue; require_astra_main_agent_for_gate_review=(!$newValue); enable_gate_reviewer=$true}
        $expected = if ($newValue) {'Off'} else {'Final'}
        Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel luna) $expected 'New key precedence'
        $count++
    }
    Save-Config @{require_sol_or_astra_main_agent_for_gate_review=$true; enable_gate_reviewer=$false; review_committed_major_milestones=$true}
    foreach ($model in @('sol','astra')) {
        Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel $model) 'Off' 'Disabled gates remain disabled'
        $count++
    }
    '{ invalid json' | Set-Content (Join-Path $tempRoot '.agents/config/config.json')
    Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel sol) 'Off' 'Invalid config'
    Remove-Item (Join-Path $tempRoot '.agents/config/config.json')
    Assert-Equal (& $scriptPath -RepositoryRoot $tempRoot -EffectiveMainAgentModel astra) 'Off' 'Missing config'
    $count += 2
    "PASS: $count gate eligibility and reviewer routing cases"
} finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force
}
