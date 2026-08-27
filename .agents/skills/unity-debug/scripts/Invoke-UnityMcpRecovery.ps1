[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8080,
    [string]$McpForUnityVersion,
    [int]$TimeoutSec = 45,
    [switch]$StatusOnly,
    [switch]$UseEditorHook,
    [string]$LaunchRecord,
    [switch]$RelaunchOnce,
    [switch]$DryRun
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

$ErrorActionPreference = "Stop"

function Write-RecoveryStatus {
    param(
        [Parameter(Mandatory = $true)][string]$State,
        [Parameter(Mandatory = $true)][string]$Message
    )

    Write-Host ("[{0}] {1}" -f $State, $Message)
}

function Test-TcpPort {
    param(
        [Parameter(Mandatory = $true)][string]$HostName,
        [Parameter(Mandatory = $true)][int]$Port,
        [int]$TimeoutMs = 1000
    )

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne($TimeoutMs)) {
            return $false
        }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

function Get-UvxPath {
    $command = Get-Command "uvx" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $userProfile = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    foreach ($localUvx in @((Join-Path $userProfile ".local/bin/uvx"), (Join-Path $userProfile ".local/bin/uvx.exe"))) {
        if (Test-Path -LiteralPath $localUvx) { return $localUvx }
    }

    throw "uvx was not found. Install uv, or place uvx under the current user's .local/bin directory."
}

function Start-McpHttpServer {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$Version
    )

    $uvxPath = Get-UvxPath
    $tempDir = Join-Path $ProjectPath "_temp"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    $stdoutLog = Join-Path $tempDir "unity_mcp_http_stdout.log"
    $stderrLog = Join-Path $tempDir "unity_mcp_http_stderr.log"
    $arguments = @(
        "--from", ("mcpforunityserver=={0}" -f $Version),
        "mcp-for-unity",
        "--transport", "http",
        "--http-url", $Endpoint,
        "--project-scoped-tools"
    )

    Write-RecoveryStatus "INFO" ("Starting MCP HTTP server with {0}" -f $uvxPath)
    $startParameters = @{ FilePath = $uvxPath; ArgumentList = $arguments; WorkingDirectory = $ProjectPath; RedirectStandardOutput = $stdoutLog; RedirectStandardError = $stderrLog; PassThru = $true }
    if ($IsWindows) { $startParameters.WindowStyle = "Hidden" }
    $process = Start-Process @startParameters

    return [pscustomobject]@{
        ProcessId = $process.Id
        StdoutLog = $stdoutLog
        StderrLog = $stderrLog
    }
}

function Get-McpProjectInstances {
    param($Instances, [Parameter(Mandatory = $true)][string]$ProjectPath)
    return @(Get-UnityMcpProjectInstances -Instances $Instances -ProjectPath $ProjectPath)
}

function Test-McpProjectInstanceUnambiguous {
    param($Instances, [Parameter(Mandatory = $true)][string]$ProjectPath)
    return $Instances -and
        (Get-McpProjectInstances -Instances $Instances -ProjectPath $ProjectPath).Count -eq 1
}

function Get-McpForUnityPackageVersion {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    $packageJson = Join-Path $ProjectPath "Packages/com.coplaydev.unity-mcp/package.json"
    if (-not (Test-Path -LiteralPath $packageJson -PathType Leaf)) {
        throw "MCP for Unity package.json was not found: $packageJson"
    }
    $package = Get-Content -Raw -Encoding UTF8 -LiteralPath $packageJson | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$package.version)) {
        throw "MCP for Unity package.json does not contain a version."
    }
    return [string]$package.version
}

function ConvertFrom-McpContent {
    param([string]$Content)

    if ([string]::IsNullOrWhiteSpace($Content)) {
        return $null
    }

    $trimmed = $Content.Trim()
    if ($trimmed.StartsWith("{")) {
        return ConvertFrom-McpJsonText -Text $trimmed
    }

    $dataLines = @()
    foreach ($line in ($trimmed -split "`r?`n")) {
        if ($line.StartsWith("data:")) {
            $dataLines += $line.Substring(5).Trim()
        }
    }

    if ($dataLines.Count -gt 0) {
        return ConvertFrom-McpJsonText -Text ($dataLines -join "`n")
    }

    throw "Unable to parse MCP response: $Content"
}

function ConvertFrom-McpJsonText {
    param([Parameter(Mandatory = $true)][string]$Text)

    try {
        return $Text | ConvertFrom-Json
    }
    catch {
        $documents = Split-McpJsonDocuments -Text $Text
        if ($documents.Count -eq 0) {
            throw
        }

        return ($documents[-1] | ConvertFrom-Json)
    }
}

function Split-McpJsonDocuments {
    param([Parameter(Mandatory = $true)][string]$Text)

    $documents = New-Object System.Collections.Generic.List[string]
    $depth = 0
    $start = -1
    $inString = $false
    $escape = $false

    for ($i = 0; $i -lt $Text.Length; $i++) {
        $char = $Text[$i]

        if ($inString) {
            if ($escape) {
                $escape = $false
                continue
            }
            if ($char -eq "\") {
                $escape = $true
                continue
            }
            if ($char -eq '"') {
                $inString = $false
            }
            continue
        }

        if ($char -eq '"') {
            $inString = $true
            continue
        }

        if ($char -eq "{" -or $char -eq "[") {
            if ($depth -eq 0) {
                $start = $i
            }
            $depth++
            continue
        }

        if ($char -eq "}" -or $char -eq "]") {
            if ($depth -gt 0) {
                $depth--
                if ($depth -eq 0 -and $start -ge 0) {
                    $documents.Add($Text.Substring($start, $i - $start + 1))
                    $start = -1
                }
            }
        }
    }

    return $documents
}

function Get-HeaderValue {
    param(
        [Parameter(Mandatory = $true)]$Headers,
        [Parameter(Mandatory = $true)][string]$Name
    )

    foreach ($key in $Headers.Keys) {
        if ([string]::Equals($key, $Name, [System.StringComparison]::OrdinalIgnoreCase)) {
            $value = $Headers[$key]
            if ($value -is [array]) {
                return $value[0]
            }
            return $value
        }
    }

    return $null
}

function Invoke-McpRaw {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)]$Payload,
        [string]$SessionId
    )

    $headers = @{
        Accept = "application/json, text/event-stream"
    }
    if ($SessionId) {
        $headers["mcp-session-id"] = $SessionId
    }

    $body = $Payload | ConvertTo-Json -Depth 20 -Compress
    $response = Invoke-WebRequest -Uri $Endpoint -Method Post -Headers $headers -ContentType "application/json" -Body $body -TimeoutSec 15
    return [pscustomobject]@{
        Response = ConvertFrom-McpContent -Content $response.Content
        SessionId = Get-HeaderValue -Headers $response.Headers -Name "mcp-session-id"
    }
}

function New-McpSession {
    param([Parameter(Mandatory = $true)][string]$Endpoint)

    $payload = [ordered]@{
        jsonrpc = "2.0"
        id = 1
        method = "initialize"
        params = [ordered]@{
            protocolVersion = "2025-06-18"
            capabilities = [ordered]@{}
            clientInfo = [ordered]@{
                name = "unity-debug-mcp-recovery"
                version = "1.0.0"
            }
        }
    }

    $result = Invoke-McpRaw -Endpoint $Endpoint -Payload $payload
    if (-not $result.SessionId) {
        throw "MCP initialize succeeded but no mcp-session-id header was returned."
    }

    try {
        $notification = [ordered]@{
            jsonrpc = "2.0"
            method = "notifications/initialized"
        }
        [void](Invoke-McpRaw -Endpoint $Endpoint -Payload $notification -SessionId $result.SessionId)
    }
    catch {
        Write-RecoveryStatus "WARN" ("MCP initialized notification failed: {0}" -f $_.Exception.Message)
    }

    return $result.SessionId
}

function Invoke-McpRequest {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId,
        [Parameter(Mandatory = $true)][string]$Method,
        $Params,
        [int]$Id = 2
    )

    $payload = [ordered]@{
        jsonrpc = "2.0"
        id = $Id
        method = $Method
    }
    if ($null -ne $Params) {
        $payload.params = $Params
    }

    $raw = Invoke-McpRaw -Endpoint $Endpoint -Payload $payload -SessionId $SessionId
    if ($raw.Response.error) {
        throw ("MCP {0} failed: {1}" -f $Method, ($raw.Response.error | ConvertTo-Json -Depth 8 -Compress))
    }

    return $raw.Response.result
}

function Read-McpResource {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId,
        [Parameter(Mandatory = $true)][string]$Uri,
        [int]$Id
    )

    $result = Invoke-McpRequest -Endpoint $Endpoint -SessionId $SessionId -Method "resources/read" -Params ([ordered]@{ uri = $Uri }) -Id $Id
    if (-not $result.contents -or $result.contents.Count -eq 0) {
        return $null
    }

    $text = $result.contents[0].text
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    return ConvertFrom-McpJsonText -Text $text
}

function Invoke-McpTool {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId,
        [Parameter(Mandatory = $true)][string]$Name,
        $Arguments,
        [int]$Id
    )

    return Invoke-McpRequest -Endpoint $Endpoint -SessionId $SessionId -Method "tools/call" -Params ([ordered]@{ name = $Name; arguments = $Arguments }) -Id $Id
}

function Select-McpProjectInstance {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId,
        $Instances,
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [int]$Id = 25
    )

    $matches = @(Get-McpProjectInstances -Instances $Instances -ProjectPath $ProjectPath)
    if ($matches.Count -ne 1) { return $null }
    $instanceId = [string]$matches[0].id
    if ([string]::IsNullOrWhiteSpace($instanceId)) {
        throw "The exact project instance has no Name@hash identifier for session-scoped routing."
    }

    $selection = Invoke-McpTool -Endpoint $Endpoint -SessionId $SessionId -Name "set_active_instance" -Arguments ([ordered]@{ instance = $instanceId }) -Id $Id
    if ($selection -and $selection.PSObject.Properties["isError"] -and [bool]$selection.isError) {
        throw "MCP rejected session routing to the exact project instance."
    }
    Write-RecoveryStatus "OK" ("Pinned this MCP session to exact instance {0}." -f $instanceId)
    return $matches[0]
}

function Test-McpReadConsole {
    param(
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId
    )

    try {
        $arguments = [ordered]@{
            action = "get"
            count = "5"
            types = @("error", "warning")
            format = "plain"
        }
        $result = Invoke-McpTool -Endpoint $Endpoint -SessionId $SessionId -Name "read_console" -Arguments $arguments -Id 60
        Write-RecoveryStatus "OK" "read_console succeeded through MCP."
        if ($result -and $result.content) {
            foreach ($item in $result.content) {
                if ($item.text) {
                    $text = $item.text.Trim()
                    if ($text) {
                        Write-Host $text
                    }
                }
            }
        }
        return $true
    }
    catch {
        Write-RecoveryStatus "WARN" ("read_console failed after editor state check: {0}" -f $_.Exception.Message)
        return $false
    }
}

function New-EditorHookContent {
    param([Parameter(Mandatory = $true)][string]$BaseUrl)

    return @"
// Generated local-only MCP bridge recovery hook from Invoke-UnityMcpRecovery.ps1.
using System;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services;
using UnityEditor;
using UnityEngine;

namespace Codex.Temp
{
    [InitializeOnLoad]
    public static class CodexMcpRecovery
    {
        static CodexMcpRecovery()
        {
            EditorApplication.delayCall += StartBridge;
        }

        private static async void StartBridge()
        {
            try
            {
                EditorPrefs.SetBool("MCPForUnity.UseHttpTransport", true);
                EditorPrefs.SetString("MCPForUnity.HttpTransportScope", "local");
                EditorPrefs.SetString("MCPForUnity.HttpUrl", "$BaseUrl");

                bool reachable = MCPServiceLocator.Server.IsLocalHttpServerReachable();
                Debug.Log("[CodexMcpRecovery] HTTP server reachable: " + reachable + " at " + HttpEndpointUtility.GetLocalBaseUrl());

                bool started = await MCPServiceLocator.Bridge.StartAsync();
                Debug.Log("[CodexMcpRecovery] Bridge start result: " + started);
            }
            catch (Exception ex)
            {
                Debug.LogError("[CodexMcpRecovery] Bridge start failed: " + ex);
            }
        }
    }
}
"@
}

function Invoke-TemporaryEditorHook {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [Parameter(Mandatory = $true)][string]$BaseUrl,
        [Parameter(Mandatory = $true)][string]$Endpoint,
        [Parameter(Mandatory = $true)][string]$SessionId,
        [Parameter(Mandatory = $true)][int]$TimeoutSec
    )

    $editorDir = Join-Path $ProjectPath "Assets\Editor"
    $hookPath = Join-Path $editorDir "CodexMcpRecovery.cs"
    $metaPath = "$hookPath.meta"
    $createdHook = $false
    $createdMeta = $false

    if ((Test-Path -LiteralPath $hookPath) -and -not ((Get-Content -Raw -LiteralPath $hookPath) -like "*Invoke-UnityMcpRecovery.ps1*")) {
        throw "Refusing to overwrite existing non-generated hook: $hookPath"
    }

    try {
        New-Item -ItemType Directory -Force -Path $editorDir | Out-Null
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($hookPath, (New-EditorHookContent -BaseUrl $BaseUrl), $encoding)
        $createdHook = $true
        Write-RecoveryStatus "INFO" ("Wrote temporary Editor hook: {0}" -f $hookPath)
        Write-RecoveryStatus "ACTION" "If Unity does not auto-refresh, trigger Assets > Refresh or press Ctrl+R in Unity."

        $deadline = (Get-Date).AddSeconds($TimeoutSec)
        do {
            Start-Sleep -Seconds 2
            $instances = Read-McpResource -Endpoint $Endpoint -SessionId $SessionId -Uri "mcpforunity://instances" -Id 40
            if (Test-McpProjectInstanceUnambiguous -Instances $instances -ProjectPath $ProjectPath) {
                Write-RecoveryStatus "OK" ("Unity bridge connected after temporary hook. Instances: {0}" -f $instances.instance_count)
                return $instances
            }
        } while ((Get-Date) -lt $deadline)

        if (Test-Path -LiteralPath $metaPath) {
            $createdMeta = $true
        }

        Write-RecoveryStatus "WARN" "Temporary hook did not produce a Unity bridge connection before timeout."
        return $null
    }
    finally {
        if ($createdHook -and (Test-Path -LiteralPath $hookPath)) {
            Remove-Item -LiteralPath $hookPath -Force
            Write-RecoveryStatus "INFO" ("Removed temporary Editor hook: {0}" -f $hookPath)
        }
        if (($createdMeta -or (Test-Path -LiteralPath $metaPath)) -and (Test-Path -LiteralPath $metaPath)) {
            Remove-Item -LiteralPath $metaPath -Force
            Write-RecoveryStatus "INFO" ("Removed temporary Editor hook meta: {0}" -f $metaPath)
        }
    }
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$McpForUnityVersion = if ([string]::IsNullOrWhiteSpace($McpForUnityVersion)) {
    Get-McpForUnityPackageVersion -ProjectPath $resolvedProjectPath
} else {
    $McpForUnityVersion
}
$baseUrl = "http://{0}:{1}" -f $HostName, $Port
$endpoint = "{0}/mcp" -f $baseUrl

Write-Host "Project: $resolvedProjectPath"
Write-Host "MCP endpoint: $endpoint"
Write-Host ("Mode: {0}" -f ($(if ($StatusOnly) { "status only" } else { "recover" })))
Write-Host ""

if ($DryRun) {
    Write-RecoveryStatus "DRY RUN" "Would probe/start the local MCP HTTP server, initialize MCP, match this project by exact path or project hash, pin the session to its Name@hash, and require read_console success."
    if ($RelaunchOnce) {
        Write-RecoveryStatus "DRY RUN" "Would verify and stop only the supplied agent-owned launch record, run mandatory preparation, and relaunch exactly once."
    }
    exit 0
}

$serverStarted = $false
if (Test-TcpPort -HostName $HostName -Port $Port) {
    Write-RecoveryStatus "OK" ("Port {0} is already listening on {1}." -f $Port, $HostName)
}
elseif ($StatusOnly) {
    Write-RecoveryStatus "FAIL" ("Port {0} is not listening on {1}. Re-run without -StatusOnly to start the MCP HTTP server." -f $Port, $HostName)
    exit 1
}
else {
    $serverInfo = Start-McpHttpServer -ProjectPath $resolvedProjectPath -Endpoint $endpoint -Version $McpForUnityVersion
    $serverStarted = $true
    Write-RecoveryStatus "INFO" ("Started process id {0}. stderr: {1}" -f $serverInfo.ProcessId, $serverInfo.StderrLog)

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    do {
        Start-Sleep -Milliseconds 500
        if (Test-TcpPort -HostName $HostName -Port $Port) {
            Write-RecoveryStatus "OK" ("MCP HTTP server is listening on {0}:{1}." -f $HostName, $Port)
            break
        }
    } while ((Get-Date) -lt $deadline)

    if (-not (Test-TcpPort -HostName $HostName -Port $Port)) {
        Write-RecoveryStatus "FAIL" "MCP HTTP server did not become reachable before timeout."
        exit 1
    }
}

try {
    $sessionId = New-McpSession -Endpoint $endpoint
    Write-RecoveryStatus "OK" ("MCP initialize succeeded. Session: {0}" -f $sessionId)

    $tools = Invoke-McpRequest -Endpoint $endpoint -SessionId $sessionId -Method "tools/list" -Params $null -Id 10
    $toolCount = 0
    if ($tools -and $tools.tools) {
        $toolCount = $tools.tools.Count
    }
    Write-RecoveryStatus "OK" ("MCP endpoint returned {0} tools." -f $toolCount)

    $instances = Read-McpResource -Endpoint $endpoint -SessionId $sessionId -Uri "mcpforunity://instances" -Id 20
    if ($instances) {
        Write-RecoveryStatus "INFO" ("Unity instances: {0}" -f $instances.instance_count)
        if ($instances.instances) {
            foreach ($instance in $instances.instances) {
                Write-Host ("  - {0} {1} {2}" -f $instance.name, $instance.project_path, $instance.unity_version)
            }
        }
    }

    $selectedProjectInstance = Select-McpProjectInstance -Endpoint $endpoint -SessionId $sessionId -Instances $instances -ProjectPath $resolvedProjectPath -Id 25
    if ($selectedProjectInstance) {
        $editorState = Read-McpResource -Endpoint $endpoint -SessionId $sessionId -Uri "mcpforunity://editor/state" -Id 30
        $readConsoleSucceeded = $false
        if ($editorState -and $editorState.success) {
            Write-RecoveryStatus "OK" "Unity editor state is readable through MCP."
            $readConsoleSucceeded = Test-McpReadConsole -Endpoint $endpoint -SessionId $sessionId
        }
        else {
            Write-RecoveryStatus "WARN" ("Unity editor state was not readable: {0}" -f ($editorState | ConvertTo-Json -Depth 8 -Compress))
        }
        if ($editorState -and $editorState.success -and $readConsoleSucceeded -and (-not $UseEditorHook -or $StatusOnly)) {
            exit 0
        }
    }

    if ($UseEditorHook -and -not $StatusOnly) {
        $instances = Invoke-TemporaryEditorHook -ProjectPath $resolvedProjectPath -BaseUrl $baseUrl -Endpoint $endpoint -SessionId $sessionId -TimeoutSec $TimeoutSec
        if (Test-McpProjectInstanceUnambiguous -Instances $instances -ProjectPath $resolvedProjectPath) {
            [void](Select-McpProjectInstance -Endpoint $endpoint -SessionId $sessionId -Instances $instances -ProjectPath $resolvedProjectPath -Id 45)
            $editorState = Read-McpResource -Endpoint $endpoint -SessionId $sessionId -Uri "mcpforunity://editor/state" -Id 50
            if ($editorState -and $editorState.success) {
                Write-RecoveryStatus "OK" "Unity editor state is readable through MCP after recovery."
                if (Test-McpReadConsole -Endpoint $endpoint -SessionId $sessionId) {
                    exit 0
                }
            }
            Write-RecoveryStatus "WARN" ("Bridge connected, but editor state was not readable: {0}" -f ($editorState | ConvertTo-Json -Depth 8 -Compress))
            exit 2
        }
    }

    if ($RelaunchOnce -and -not $StatusOnly) {
        if ([string]::IsNullOrWhiteSpace($LaunchRecord)) {
            Write-RecoveryStatus "FAIL" "-RelaunchOnce requires the launch record of an agent-owned Editor."
            exit 1
        }

        $powerShell = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
        if (-not $powerShell) { $powerShell = (Get-Command powershell -ErrorAction SilentlyContinue).Source }
        if (-not $powerShell) { Write-RecoveryStatus "FAIL" "PowerShell executable was not found for guarded relaunch."; exit 1 }

        Write-RecoveryStatus "INFO" "Stopping only the Editor verified by the supplied agent launch record."
        & $powerShell -NoProfile -File (Join-Path $PSScriptRoot "Stop-AgentUnityEditor.ps1") -LaunchRecord $LaunchRecord -AsJson | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-RecoveryStatus "FAIL" "The agent-owned Editor could not be verified and stopped; no relaunch was attempted."; exit 1 }

        Write-RecoveryStatus "INFO" "Running mandatory preparation and performing the single allowed relaunch."
        $launchOutput = & $powerShell -NoProfile -File (Join-Path $PSScriptRoot "Start-UnityEditor.ps1") -ProjectPath $resolvedProjectPath -AsJson
        if ($LASTEXITCODE -ne 0) { Write-RecoveryStatus "FAIL" "The guarded relaunch was blocked."; exit 1 }
        $launch = (($launchOutput | Out-String).Trim() | ConvertFrom-Json)
        Write-RecoveryStatus "INFO" ("Single guarded relaunch record: {0}" -f $launch.launchRecord)

        if ($launch.startupEvidence -eq "safe-mode-window") {
            Write-RecoveryStatus "ACTION" "Unity requested Safe Mode. Use accessibility state on this exact project window and choose Enter Safe Mode; never choose Ignore."
            exit 3
        }

        # The ownership stop may have terminated the old project-scoped server, so its
        # MCP session id must never be reused against the replacement server.
        $relaunchSessionId = New-McpSession -Endpoint $endpoint

        $deadline = (Get-Date).AddSeconds($TimeoutSec)
        do {
            Start-Sleep -Seconds 2
            if ($launch.launchLog -and (Test-Path -LiteralPath $launch.launchLog)) {
                $launchText = Get-Content -Raw -Encoding UTF8 -LiteralPath $launch.launchLog
                if ($launchText -match 'Safe Mode:|Enter Safe Mode') {
                    Write-RecoveryStatus "ACTION" "Unity entered or requested Safe Mode. Use accessibility state on this exact project window and choose Enter Safe Mode; never choose Ignore."
                    exit 3
                }
            }
            $instances = Read-McpResource -Endpoint $endpoint -SessionId $relaunchSessionId -Uri "mcpforunity://instances" -Id 60
            if (Test-McpProjectInstanceUnambiguous -Instances $instances -ProjectPath $resolvedProjectPath) {
                Write-RecoveryStatus "OK" "The exact project connected after the single guarded relaunch."
                [void](Select-McpProjectInstance -Endpoint $endpoint -SessionId $relaunchSessionId -Instances $instances -ProjectPath $resolvedProjectPath -Id 65)
                if (Test-McpReadConsole -Endpoint $endpoint -SessionId $relaunchSessionId) {
                    exit 0
                }
            }
        } while ((Get-Date) -lt $deadline)

        Write-RecoveryStatus "FAIL" "The exact project did not connect after the single guarded relaunch; no further retry was attempted."
        exit 2
    }

    Write-RecoveryStatus "ACTION" "MCP HTTP server is available, but no Unity bridge session is connected."
    Write-RecoveryStatus "ACTION" "Open the MCP for Unity window and connect, or re-run this script with -UseEditorHook and refresh Unity if needed."
    if ($serverStarted) {
        Write-RecoveryStatus "INFO" "The MCP HTTP server was left running for the next Codex session or manual bridge connection."
    }
    exit 2
}
catch {
    Write-RecoveryStatus "FAIL" $_.Exception.Message
    exit 1
}
