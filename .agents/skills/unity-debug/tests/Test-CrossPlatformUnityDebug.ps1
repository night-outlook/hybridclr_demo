[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$skillRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
. (Join-Path $skillRoot "scripts/UnityDebug.Common.ps1")

function Assert-UnityDebugTest {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

$repoRoot = Get-UnityDebugSkillBasePath
$repositoryConfig = Read-UnityDebugJson -Path (Join-Path $repoRoot ".agents/config/config.json")
Assert-UnityDebugTest (Test-UnityVisibleEditorLaunchPermissionValue $repositoryConfig) "Repository launch permission must be true."
Assert-UnityDebugTest (-not (Test-UnityVisibleEditorLaunchPermissionValue ([pscustomobject]@{ unity_debug = [pscustomobject]@{ allow_agent_to_launch_visible_editor = 1 } }))) "Invalid permission must fail closed."
Assert-UnityDebugTest (-not (Test-UnityVisibleEditorLaunchPermissionValue ([pscustomobject]@{ unity_debug = [pscustomobject]@{ allow_agent_to_launch_visible_editor = $false } }))) "False repository permission must block launch."
Assert-UnityDebugTest ((Get-UnityVisibleEditorLaunchPermission -RepositoryRoot $repoRoot).ConfigPath -eq (Join-Path $repoRoot ".agents/config/config.json")) "Visible launch permission did not read the repository config."

$quotedProject = Join-Path ([System.IO.Path]::GetTempPath()) "Unity Project"
$parsedProject = Get-UnityProjectPathFromCommandLine "Unity -projectPath `"$quotedProject`" -batchmode"
Assert-UnityDebugTest (Test-UnityPathEqual $quotedProject $parsedProject) "Quoted project parsing failed."
Assert-UnityDebugTest (-not (Test-UnityPathEqual $quotedProject "$quotedProject-other")) "Exact-project comparison accepted a prefix."

$projectHash = Get-UnityProjectIdentityHash -ProjectPath $quotedProject
$hashInstances = [pscustomobject]@{ instances = @([pscustomobject]@{ id = "Unity Project@$projectHash"; name = "Unity Project"; hash = $projectHash }) }
Assert-UnityDebugTest (@(Get-UnityMcpProjectInstances -Instances $hashInstances -ProjectPath $quotedProject).Count -eq 1) "Hash-only exact-project MCP matching failed."
$wrongHashInstances = [pscustomobject]@{ instances = @([pscustomobject]@{ id = "Unity Project@wrong"; name = "Unity Project"; hash = "wrong" }) }
Assert-UnityDebugTest (@(Get-UnityMcpProjectInstances -Instances $wrongHashInstances -ProjectPath $quotedProject).Count -eq 0) "MCP matching trusted a project name with the wrong hash."

$lowMemory = [pscustomobject]@{ Succeeded = $true; AvailableGB = 3.99 }
Assert-UnityDebugTest (Test-UnityEditorMemoryGate $lowMemory 0).Allowed "Zero-Editor memory policy applied an unwanted fixed threshold."
Assert-UnityDebugTest (-not (Test-UnityEditorMemoryGate $lowMemory 1).Allowed) "One-Editor memory policy did not require 4 GB."
Assert-UnityDebugTest (Test-UnityEditorMemoryGate ([pscustomobject]@{ Succeeded = $true; AvailableGB = 4.0 }) 3).Allowed "Multiple-Editor 4 GB boundary failed."
Assert-UnityDebugTest (-not (Test-UnityEditorMemoryGate ([pscustomobject]@{ Succeeded = $false; AvailableGB = $null }) 0).Allowed) "Failed memory probe did not fail closed."

Assert-UnityDebugTest (-not (Test-UnityStartupReadinessState $true $true $false 30 10)) "Startup succeeded without automation-ready evidence."
Assert-UnityDebugTest (-not (Test-UnityStartupReadinessState $true $true $true 9.9 10)) "Startup succeeded before evidence was stable."
Assert-UnityDebugTest (-not (Test-UnityStartupReadinessState $false $true $true 10 10)) "Startup succeeded after process exit."
Assert-UnityDebugTest (-not (Test-UnityStartupReadinessState $true $false $true 10 10)) "Startup succeeded without exact-project ownership."
Assert-UnityDebugTest (Test-UnityStartupReadinessState $true $true $true 10 10) "Stable automation-ready evidence was rejected."
Assert-UnityDebugTest ((Get-UnityWindowEvidenceKind @("Main - /tmp/My Project", "Enter Safe Mode?") "/tmp/My Project") -eq "safe-mode-window") "Safe Mode did not take priority over the normal project window."
Assert-UnityDebugTest ((Get-UnityWindowEvidenceKind @("Main - /tmp/My Project") "/tmp/My Project") -eq "project-window") "Exact-project window evidence was not recognized."

$formatted = Format-NativeArgumentList @("-projectPath", $quotedProject)
Assert-UnityDebugTest ($formatted -match '^-projectPath ".+Unity Project"$') "Native argument quoting failed."
$expectedUtcStart = [datetime]::Parse("2026-08-19T08:57:32.4652230Z").ToUniversalTime()
$jsonUtcStart = (@{ value = $expectedUtcStart.ToString("o") } | ConvertTo-Json | ConvertFrom-Json).value
Assert-UnityDebugTest ((ConvertTo-UnityDebugUtcDateTime -Value $jsonUtcStart) -eq $expectedUtcStart) "JSON DateTime deserialization changed process-start ownership identity."
$pidFile = Join-Path $quotedProject "Library/MCPForUnity/RunState/mcp_http_8080.pid"
$validServerCommand = "python mcp-for-unity --transport http --pidfile `"$pidFile`" --unity-instance-token token"
Assert-UnityDebugTest (Test-UnityMcpServerCommandLine -CommandLine $validServerCommand -PidFilePath $pidFile) "Project-scoped MCP server command contract was rejected."
Assert-UnityDebugTest (-not (Test-UnityMcpServerCommandLine -CommandLine ($validServerCommand -replace '--unity-instance-token token', '') -PidFilePath $pidFile)) "MCP ownership accepted a command without an instance token."
$malformedMcpRecord = [pscustomobject]@{ schemaVersion = "invalid"; owner = "not-agent"; pid = "invalid"; port = "invalid"; projectPath = $quotedProject; pidFilePath = $pidFile; processStartTimeUtc = "invalid"; commandLineSha256 = "invalid" }
Assert-UnityDebugTest (-not (Stop-UnityMcpServerFromOwnershipRecord -Record $malformedMcpRecord -DryRun).ok) "Malformed MCP ownership record did not fail closed."

$findSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Find-Unity.ps1")
$commonSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/UnityDebug.Common.ps1")
$startSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Start-UnityEditor.ps1")
Assert-UnityDebugTest ($commonSource -match '"/usr/bin/open"') "Visible macOS Editor launch does not use LaunchServices."
Assert-UnityDebugTest ($commonSource -match 'Get-UnityProjectProcesses -ProjectPath \$ProjectPath') "Visible macOS Editor launch does not resolve the exact project PID."
Assert-UnityDebugTest ($startSource -match 'Start-UnityVisibleEditorProcess') "Visible Editor script bypasses the platform launch contract."
Assert-UnityDebugTest ($findSource.Contains('/Applications/Unity/Hub/Editor/$Version/Unity.app/Contents/MacOS/Unity')) "macOS Hub discovery path is missing."
$prepareSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Prepare-UnityEditorLaunch.ps1")
Assert-UnityDebugTest ($prepareSource.Contains('Stop-Process -Id $process.Id -Force')) "Timed-out batch cleanup is missing."
$stopSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Stop-AgentUnityEditor.ps1")
Assert-UnityDebugTest ($stopSource.Contains('processStartTimeUtc') -and $stopSource.Contains('owner')) "Launch-record ownership verification is incomplete."
Assert-UnityDebugTest ($startSource.Contains('Get-UnityMcpServerOwnershipRecord') -and $startSource.Contains('$record.mcpServer')) "Visible launch does not record strongly verified new MCP ownership."
Assert-UnityDebugTest ($startSource.Contains('Relevant project source changed after mandatory preparation')) "Visible launch does not recheck source freshness after preparation."
Assert-UnityDebugTest ($stopSource.Contains('Stop-UnityMcpServerFromOwnershipRecord')) "Record-only shutdown does not clean a verified owned MCP server."
$recoverySource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Invoke-UnityMcpRecovery.ps1")
Assert-UnityDebugTest ($recoverySource.Contains('Get-McpForUnityPackageVersion')) "MCP recovery does not derive the embedded server version."
Assert-UnityDebugTest ($recoverySource.Contains('set_active_instance')) "MCP recovery does not pin routing to the exact project instance."
Assert-UnityDebugTest ($recoverySource.Contains('Test-McpReadConsole')) "MCP recovery does not require a real console operation."
Assert-UnityDebugTest ($recoverySource.Contains('$relaunchSessionId = New-McpSession')) "Guarded relaunch reuses a stale MCP session id."
Assert-UnityDebugTest ($recoverySource -notmatch 'instance_count -eq 1') "MCP recovery still rejects other connected Editors globally."

$compileSource = Get-Content -Raw -Encoding UTF8 (Join-Path $skillRoot "scripts/Invoke-UnityCompile.ps1")
Assert-UnityDebugTest ($compileSource.Contains('Get-UnityDebugActionableConsoleErrorCount')) "Unity compile report bypasses the stale-runtime console policy."
$staleRuntimeErrors = @("old runtime error", "old runtime stack")
Assert-UnityDebugTest ((Get-UnityDebugActionableConsoleErrorCount -ConsoleErrors $staleRuntimeErrors -RuntimeStaleLogNotices @("stale runtime log")) -eq 0) "Stale runtime console errors still fail compile verification."
Assert-UnityDebugTest ((Get-UnityDebugActionableConsoleErrorCount -ConsoleErrors $staleRuntimeErrors -RuntimeStaleLogNotices @()) -eq 2) "Fresh runtime console errors no longer fail compile verification."

Write-Host "[PASS] Cross-platform Unity debug policy tests completed."
