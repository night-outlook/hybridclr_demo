$scripts = Join-Path $PSScriptRoot "../scripts"
. (Join-Path $scripts "UnityDebug.Common.ps1")

Describe "guarded cross-platform Unity Editor launch" {
    It "fails closed for missing and invalid permission and accepts only boolean true" {
        (Test-UnityVisibleEditorLaunchPermissionValue -Config ([pscustomobject]@{})) | Should -BeFalse
        (Test-UnityVisibleEditorLaunchPermissionValue -Config ([pscustomobject]@{ unity_debug = [pscustomobject]@{ allow_agent_to_launch_visible_editor = "true" } })) | Should -BeFalse
        (Test-UnityVisibleEditorLaunchPermissionValue -Config ([pscustomobject]@{ unity_debug = [pscustomobject]@{ allow_agent_to_launch_visible_editor = $false } })) | Should -BeFalse
        (Test-UnityVisibleEditorLaunchPermissionValue -Config ([pscustomobject]@{ unity_debug = [pscustomobject]@{ allow_agent_to_launch_visible_editor = $true } })) | Should -BeTrue
    }

    It "extracts and compares the exact project path without exposing unrelated arguments" {
        $path = Get-UnityProjectPathFromCommandLine -CommandLine '/Applications/Unity -projectPath "/tmp/My Project" -accessToken secret'
        $path | Should -Be ([System.IO.Path]::GetFullPath("/tmp/My Project"))
        (Test-UnityPathEqual $path "/tmp/My Project") | Should -BeTrue
        (Test-UnityPathEqual $path "/tmp/My Project 2") | Should -BeFalse
    }

    It "matches an MCP instance by the package-compatible project hash without trusting its name" {
        $project = [System.IO.Path]::GetFullPath("/tmp/Unity Project")
        $hash = Get-UnityProjectIdentityHash -ProjectPath $project
        $instances = [pscustomobject]@{
            instances = @(
                [pscustomobject]@{ id = "Unity Project@$hash"; name = "Unity Project"; hash = $hash },
                [pscustomobject]@{ id = "Unity Project@wrong"; name = "Unity Project"; hash = "wrong" }
            )
        }
        @(Get-UnityMcpProjectInstances -Instances $instances -ProjectPath $project).Count | Should -Be 1
        @(Get-UnityMcpProjectInstances -Instances ([pscustomobject]@{ instances = @($instances.instances[1]) }) -ProjectPath $project).Count | Should -Be 0
    }

    It "applies no fixed threshold with zero Editors and four GB with one or more" {
        $low = [pscustomobject]@{ Succeeded = $true; AvailableGB = 3.99 }
        (Test-UnityEditorMemoryGate -Memory $low -OtherEditorCount 0).Allowed | Should -BeTrue
        (Test-UnityEditorMemoryGate -Memory $low -OtherEditorCount 1).Allowed | Should -BeFalse
        (Test-UnityEditorMemoryGate -Memory ([pscustomobject]@{ Succeeded = $true; AvailableGB = 4.0 }) -OtherEditorCount 2).Allowed | Should -BeTrue
        (Test-UnityEditorMemoryGate -Memory ([pscustomobject]@{ Succeeded = $false; AvailableGB = $null }) -OtherEditorCount 0).Allowed | Should -BeFalse
    }

    It "quotes native arguments containing whitespace" {
        (Format-NativeArgumentList @("-projectPath", "/tmp/My Project")) | Should -Be '-projectPath "/tmp/My Project"'
    }

    It "preserves UTC process-start identity after JSON DateTime deserialization" {
        $expected = [datetime]::Parse("2026-08-19T08:57:32.4652230Z").ToUniversalTime()
        $roundTripped = (@{ value = $expected.ToString("o") } | ConvertTo-Json | ConvertFrom-Json).value
        (ConvertTo-UnityDebugUtcDateTime -Value $roundTripped) | Should -Be $expected
    }

    It "accepts only a new sole MCP listener with the exact project pidfile contract" {
        $project = Join-Path $TestDrive "Project"
        $pidFile = Join-Path $project "Library/MCPForUnity/RunState/mcp_http_8080.pid"
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $pidFile) | Out-Null
        Set-Content -LiteralPath $pidFile -Value "4242" -NoNewline
        $started = (Get-Date).ToUniversalTime()
        $command = "python mcp-for-unity --transport http --pidfile `"$pidFile`" --unity-instance-token token"

        Mock Get-UnityMcpServerPidFilePath { $pidFile }
        Mock Get-UnityDebugListeningProcessIds { @(4242) }
        Mock Get-Process { [pscustomobject]@{ StartTime = $started.ToLocalTime() } } -ParameterFilter { $Id -eq 4242 }
        Mock Get-UnityDebugProcessCommandLine { $command }

        $record = Get-UnityMcpServerOwnershipRecord -ProjectPath $project -Port 8080 -PreexistingProcessIds @() -NotBeforeUtc $started.AddSeconds(-1)
        $record.pid | Should -Be 4242
        $record.owner | Should -Be "agent-unity-launch"
        $record.PSObject.Properties.Name | Should -Not -Contain "commandLine"
        (Get-UnityMcpServerOwnershipRecord -ProjectPath $project -Port 8080 -PreexistingProcessIds @(4242) -NotBeforeUtc $started.AddSeconds(-1)) | Should -BeNullOrEmpty
        (Stop-UnityMcpServerFromOwnershipRecord -Record $record -DryRun).ok | Should -BeTrue
    }

    It "fails closed for a malformed MCP ownership record even when its PID is absent" {
        $project = Join-Path $TestDrive "Project"
        $record = [pscustomobject]@{
            schemaVersion = "invalid"
            owner = "not-agent"
            pid = "invalid"
            port = "invalid"
            projectPath = $project
            pidFilePath = Join-Path $project "not-owned.pid"
            processStartTimeUtc = "invalid"
            commandLineSha256 = "invalid"
        }
        $result = Stop-UnityMcpServerFromOwnershipRecord -Record $record -DryRun
        $result.ok | Should -BeFalse
        $result.blockers.Count | Should -BeGreaterThan 0
    }

    It "requires sustained exact-project automation-ready evidence" {
        (Test-UnityStartupReadinessState -ProcessAlive $true -ExactProjectOwned $true -HasAutomationReadyEvidence $false -EvidenceStableSeconds 30) | Should -BeFalse
        (Test-UnityStartupReadinessState -ProcessAlive $true -ExactProjectOwned $true -HasAutomationReadyEvidence $true -EvidenceStableSeconds 9.9 -RequiredStableSeconds 10) | Should -BeFalse
        (Test-UnityStartupReadinessState -ProcessAlive $false -ExactProjectOwned $true -HasAutomationReadyEvidence $true -EvidenceStableSeconds 10) | Should -BeFalse
        (Test-UnityStartupReadinessState -ProcessAlive $true -ExactProjectOwned $false -HasAutomationReadyEvidence $true -EvidenceStableSeconds 10) | Should -BeFalse
        (Test-UnityStartupReadinessState -ProcessAlive $true -ExactProjectOwned $true -HasAutomationReadyEvidence $true -EvidenceStableSeconds 10) | Should -BeTrue
    }

    It "prioritizes Safe Mode over the normal project window for the exact PID" {
        (Get-UnityWindowEvidenceKind -Titles @("Main - /tmp/My Project", "Enter Safe Mode?") -ProjectPath "/tmp/My Project") | Should -Be "safe-mode-window"
        (Get-UnityWindowEvidenceKind -Titles @("Main - /tmp/My Project") -ProjectPath "/tmp/My Project") | Should -Be "project-window"
    }

    It "contains bounded timeout cleanup and launch-record ownership checks" {
        (Get-Content -Raw (Join-Path $scripts "Prepare-UnityEditorLaunch.ps1")) | Should -Match 'WaitForExit\(\$TimeoutSec \* 1000\)'
        (Get-Content -Raw (Join-Path $scripts "Stop-AgentUnityEditor.ps1")) | Should -Match 'owner.*agent'
        (Get-Content -Raw (Join-Path $scripts "Stop-AgentUnityEditor.ps1")) | Should -Match 'processStartTimeUtc'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'Get-UnityVisibleWindowEvidence'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'Test-UnityMcpEvidence'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match '\$windowEvidence\.Kind -eq "safe-mode-window"'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'A normal project window alone is not automation-ready'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'Start-UnityVisibleEditorProcess'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'visible launch failed before exact-project process ownership'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'Get-UnityMcpServerOwnershipRecord'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match '\$record\.mcpServer'
        (Get-Content -Raw (Join-Path $scripts "Start-UnityEditor.ps1")) | Should -Match 'Relevant project source changed after mandatory preparation'
        (Get-Content -Raw (Join-Path $scripts "Stop-AgentUnityEditor.ps1")) | Should -Match 'Stop-UnityMcpServerFromOwnershipRecord'
        $recoverySource = Get-Content -Raw (Join-Path $scripts "Invoke-UnityMcpRecovery.ps1")
        $recoverySource | Should -Match 'Get-McpForUnityPackageVersion'
        $recoverySource | Should -Match 'set_active_instance'
        $recoverySource | Should -Match 'Test-McpReadConsole'
        $recoverySource | Should -Match '\$relaunchSessionId = New-McpSession'
        $recoverySource | Should -Not -Match 'instance_count -eq 1'
        (Get-Content -Raw (Join-Path $scripts "UnityDebug.Common.ps1")) | Should -Match '"/usr/bin/open"'
        (Get-Content -Raw (Join-Path $scripts "UnityDebug.Common.ps1")) | Should -Match 'Get-UnityProjectProcesses -ProjectPath \$ProjectPath'
    }
}
