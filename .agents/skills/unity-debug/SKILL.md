---
name: unity-debug
description: Debug this Unity project from PowerShell and Unity MCP on Windows or macOS. Use when Codex needs to inspect Unity compile or console errors, check whether the current project is open in Unity, control a running Unity Editor through MCP, locate or configure Unity, trigger a batchmode compile, or run a Unity -executeMethod C# static method for diagnostics.
---

# Unity Debug

Use this skill for Unity debugging from the Unity project root. This repository is an empty Unity project, so the skill supports generic scenes, Assets, Packages, Editor, batchmode, and MCP operations; source-project business methods and gameplay flows are not available.

## Quick Start

Check current Unity status and recent error logs:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityCompile.ps1 -Status
```

Find or configure the Unity executable. The helper discovers both Windows Hub installs and `/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity`:

```powershell
.\.agents\skills\unity-debug\scripts\Find-Unity.ps1
.\.agents\skills\unity-debug\scripts\Find-Unity.ps1 -Set "C:\Program Files\Unity\Hub\Editor\2022.3.62f2\Editor\Unity.exe"
./.agents/skills/unity-debug/scripts/Find-Unity.ps1 -Set "/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app"
```

Start the project in a visible Unity Editor window (not batchmode), opening `Assets/Scenes/SampleScene.unity`:

```powershell
.\.agents\skills\unity-debug\scripts\Start-UnityEditor.ps1
```

Visible launch is fail-closed. `unity_debug.allow_agent_to_launch_visible_editor` must resolve to boolean `true` in the repository `.agents/config/config.json`; this does not restrict control of an already-open Editor. Memory measurement must succeed. With no other Editor there is no fixed threshold; with one or more other Editors at least 4 GB must be available. `-ForceLowMemory` is only for an explicit user-approved OOM-risk override.

Before every real visible launch, `Start-UnityEditor.ps1` invokes `Prepare-UnityEditorLaunch.ps1` exactly once. Preparation runs Unity batchmode without `-ignoreCompilerErrors`, requires fresh clean compiler evidence, and calls `MCPForUnity.Editor.McpCiBoot.EnableHttpAutoConnectForCurrentProject` to select local HTTP and enable only this project's AutoConnect preference.

Preview the command without launching Unity:

```powershell
.\.agents\skills\unity-debug\scripts\Start-UnityEditor.ps1 -DryRun
```

Check current errors without opening another Unity instance:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityCompile.ps1 -CheckOnly
```

Use structured output and fail on stale logs for automation wrappers:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityCompile.ps1 -CheckOnly -AsJson -FailOnStale
```

Recover Unity MCP for a running Editor before falling back to logs:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityMcpRecovery.ps1 -StatusOnly
.\.agents\skills\unity-debug\scripts\Invoke-UnityMcpRecovery.ps1
```

Start a clean runtime repro capture before asking the user to reproduce a Unity console issue:

```powershell
.\.agents\skills\unity-debug\scripts\Start-UnityConsoleRepro.ps1
```

Scan Unity text assets for script references by script name or GUID:

```powershell
.\.agents\skills\unity-debug\scripts\Find-UnityScriptReferences.ps1 -ScriptName GuideAnimatorListener,GuideNodeRegister
.\.agents\skills\unity-debug\scripts\Find-UnityScriptReferences.ps1 -Guid 7ef284949ace419d89a2565c0ae3937c -AsJson
```

Trigger a batchmode compile when this project is not already open in Unity:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityCompile.ps1 -TimeoutSec 300
```

Run a Unity static method:

```powershell
.\.agents\skills\unity-debug\scripts\Invoke-UnityMethod.ps1 Namespace.Class.Method
```

## Workflow

1. Check whether the current project is already open in Unity.
2. If Unity is running for the current project, do not launch another Unity instance. Prefer Unity MCP when it has an active Unity session; otherwise read `Logs\_compiler_errors.log` and `Logs\_console_errors.log`.
3. If Unity is not running, choose the execution mode: use `Start-UnityEditor.ps1` for interactive gameplay, scene, UI, or runtime repro work; use `Invoke-UnityCompile.ps1` or `Invoke-UnityMethod.ps1` only for unattended batchmode work.
4. Ensure the Unity executable is configured by running `Find-Unity.ps1` before starting either mode.
5. Inspect script output and the generated log in `_temp`.

Other Unity projects can be open. Exact-project detection uses the parsed `-projectPath` plus `Temp\UnityLockfile`; helpers never print raw process command lines. Do not treat a leftover lock file that can be opened exclusively as running.

## Unity MCP Path

Use Unity MCP only when the current project is already open in Unity and an actual MCP operation succeeds. `manage_editor(action="telemetry_ping")` can show that the service is reachable, but it is not enough to prove a usable Unity session exists. Confirm with an operation such as:

```text
read_console(action="get", count="10", types=["error","warning"], format="plain")
```

If MCP returns `no_unity_session`, times out, or fails, fall back to the PowerShell/log-file path.

If Unity is running for this project and MCP tools are unavailable, follow this order:

1. Run `.\.agents\skills\unity-debug\scripts\Invoke-UnityMcpRecovery.ps1 -StatusOnly` before using log-only fallback. If the HTTP server is absent, run `Invoke-UnityMcpRecovery.ps1` to start the server version declared by the embedded `com.coplaydev.unity-mcp/package.json`, initialize the local HTTP endpoint, and query `mcpforunity://instances`.
2. For stdio transport, the package uses `uvx ... mcp-for-unity --transport stdio`; `StdioBridgeHost` writes `%USERPROFILE%\.unity-mcp\unity-mcp-status-<hash>.json` and auto-starts when `MCPForUnity.UseHttpTransport` is false. `McpCiBoot.StartStdioForCi()` sets that pref false and calls `StdioBridgeHost.StartAutoConnect()`.
3. For HTTP transport, visible-launch preparation selects local HTTP and enables the current project's scoped AutoConnect setting. It deliberately does not enable the machine-global `MCPForUnity.AutoStartOnLoad` preference.
4. Match `mcpforunity://instances` to this exact project by canonical `project_path` when present, otherwise by the package-compatible SHA-1 project hash in `hash` or the `Name@hash` identifier. Never match by project name alone. Pin the MCP session with `set_active_instance` before reading Editor state or invoking tools, so other connected Editors remain safe. For an Editor started by the Agent, pass its record to `Invoke-UnityMcpRecovery.ps1 -LaunchRecord <path> -RelaunchOnce`; it may stop only that verified PID, rerun mandatory preparation, and relaunch once. There is no retry loop. `-UseEditorHook` is reserved for explicit recovery of a pre-existing Editor.
5. MCP readiness requires the exact instance, a readable Editor-state resource, and a successful `read_console` operation. Merely seeing a listener, tools, or an instance is insufficient. Then use first-class MCP tools if the current Codex session exposes them, or continue with direct HTTP MCP if needed.
6. If MCP is still unavailable, use the safe running-editor fallback: ask the user to trigger Unity `Assets > Refresh` / `Ctrl+R`, wait for compilation, then run `Invoke-UnityCompile.ps1 -CheckOnly` and read `Logs\_compiler_errors.log` / `Logs\_console_errors.log`.
7. Never launch Unity batchmode while this project Editor is open.

When MCP is usable:

1. Read current errors with `read_console` before reading log files.
2. Use `execute_code` for small Editor-side diagnostics that would otherwise require adding temporary scripts.
3. Use `refresh_unity` to request asset refresh or script compilation from the running Editor.
4. Before every `manage_editor(action="play")`, read one fresh `mcpforunity://editor/state` resource snapshot and pass its raw `data` object JSON to `Test-UnityPlayReadiness.ps1`. Exit `0` is the only state that permits Play. Exit `2` means blocked and exit `1` means malformed; direct Play is forbidden in either case. Explicitly refresh or wait as appropriate, read a new snapshot, and rerun the gate rather than reusing a blocked snapshot. The checker is read-only and accepts either `-StateJson` or `-StatePath`; use `-AsJson` for `ready`, `blockingReasons`, `observedAtUnixMs`, and `observedAgeMs`. The gate is strict: `advice.ready_for_tools` must be true, `staleness.is_stale` must be false, and `advice.blocking_reasons` must be an empty string array. There is no transport-latency or age waiver. Malformed age, blockers, or refresh flags, plus any refresh/import, compilation, reload, tests, Play, external changes, or advice blocker, fail closed.
5. Use specialized MCP tools when relevant: `run_tests`/`get_test_job` for Unity tests, `manage_scene` for scene state, `manage_build` for build configuration, and `manage_camera` for screenshots.

Do not call Unity batchmode while this project is already open in Unity. MCP and Editor logs are the safe control/read paths for a running Editor.

## Visible Editor Gameplay Flow

Use this flow when gameplay must be exercised in the Editor rather than compiled in batchmode:

1. Run `Start-UnityEditor.ps1` only when this project is not already open. It enforces permission, exact-project ownership, memory, and mandatory batchmode preparation. On macOS it launches the visible app through LaunchServices and then resolves the exact project PID, avoiding ownership by the short-lived PowerShell host. Launch success additionally requires exact-project MCP evidence to remain stable for the bounded startup window. The only UI-only success state is an exact-PID Safe Mode window, so the agent can safely choose **Enter Safe Mode**; a normal project window or initialization log marker alone is insufficient. Only then does it write an ignored `_temp/UnityEditorAgentLaunch_<pid>.json` ownership record and dedicated launch log. If this launch created a new project-scoped MCP server, the record includes that server only after verifying its project pidfile, sole listening PID, process start time, command contract, and fingerprint; a pre-existing server is never adopted. `Stop-AgentUnityEditor.ps1` revalidates and stops only recorded ownership, including a recorded MCP server left after the Editor has already exited. Never terminate a pre-existing or ambiguous Editor or server.
2. Inspect the correct project window through Computer Use accessibility state, never screen coordinates. If `Enter Safe Mode?` appears, choose **Enter Safe Mode**. Never choose **Ignore** or force **Exit Safe Mode** while errors remain. Read the dedicated launch log, fix only in-scope compiler errors, and wait for Unity to exit Safe Mode automatically. If the correct window cannot be distinguished or accessibility control is unavailable, stop.
3. Wait for import/compilation, then run `Invoke-UnityMcpRecovery.ps1 -StatusOnly`. If the exact project bridge is missing for an agent-owned launch, use the single guarded relaunch contract described above.
4. With a usable MCP session, use `manage_scene` to confirm or open `Assets/Scenes/SampleScene.unity`. Immediately before `manage_editor(action="play")`, read `mcpforunity://editor/state`, serialize only its raw `data` object, and require `Test-UnityPlayReadiness.ps1 -StateJson <json> -AsJson` to exit `0`. On a blocked or malformed result, do not enter Play: explicitly refresh or wait, read a new state snapshot, and rerun the gate.
5. Use MCP to inspect generic scene objects, components, and console output. Do not expect source-project gameplay views or login controls in this empty project.
7. Stop Play mode on completion or failure unless the caller asks to leave it running. Leave the Editor window open by default.

Do not use screen coordinates, hard-code credentials, print stored account values, or attempt this flow against a production login environment. The Random Account action must be invoked through the view's named UI control or an equivalent project-supported runtime action.

## Harness Resilience

Unity startup, import, and MCP recovery can exceed a default command timeout. When invoking `Invoke-UnityMcpRecovery.ps1 -UseEditorHook -TimeoutSec N`, give the outer command at least `N + 60` seconds. If the host interrupts the command, check `Assets/Editor/CodexMcpRecovery.cs` and its `.meta`; remove only those Codex-generated temporary files, then verify the Editor compiler log before continuing. `Find-Unity.ps1` also searches `%USERPROFILE%\App\Unity` for per-user editor installations before requiring `-Set`.

## Runtime Console Repro Workflow

When debugging runtime console errors that require a user action in the Unity Editor:

1. Run `Start-UnityConsoleRepro.ps1` before the repro step. It archives existing `Logs\_compiler_errors.log` and `Logs\_console_errors.log` into `_temp`, clears both logs, and writes `_temp\UnityDebug_ReproMarker.json`.
2. Ask the user to reproduce the issue in Unity.
3. Run `Invoke-UnityCompile.ps1 -CheckOnly`.
4. Treat console errors older than the repro marker as stale. The check output reports the marker timestamp and warns when `Logs\_console_errors.log` predates it.

Use `Start-UnityConsoleRepro.ps1 -NoArchive` only when preserving the prior error logs is unnecessary.

## Configuration

`config.json` is repository-level configuration and can be committed. Keep only stable fields such as `version` and `project_path` in this file.

`config.local.json` stores local machine state such as the Unity executable, `last_updated`, and `last_compilation`; keep it ignored by Git. The committed repository launch permission is under `.agents/config/config.json`; missing, malformed, or unresolved values mean `false`.

The project uses Unity `2022.3.62f2`, also recorded in `ProjectSettings\ProjectVersion.txt`.

## Error Logs

For a running Unity Editor, use the Editor-side error files:

```powershell
Get-Content Logs\_compiler_errors.log -ErrorAction SilentlyContinue
Get-Content Logs\_console_errors.log -ErrorAction SilentlyContinue
```

For batchmode debugging, use the latest Unity batchmode log and console error file:

```powershell
Get-ChildItem _temp\UnityCompile_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content Logs\_console_errors.log -ErrorAction SilentlyContinue
```

Compilation errors have priority over runtime console errors. Report file paths, line numbers, and the smallest likely fix when errors are actionable.

`Invoke-UnityCompile.ps1` filters known external Unity MCP handshake noise into `Ignored console noise` so project error counts stay actionable; inspect ignored lines only when debugging the MCP integration itself.

Do not use `Logs\_compiler_errors.log` for batchmode checks; Unity can leave it empty or stale while reporting C# compiler errors in `_temp\UnityCompile_*.log`. Do use it when the current project is already open in Unity Editor.

`Invoke-UnityCompile.ps1 -Status` and `-CheckOnly` print timestamps for the Editor-side and batchmode logs they inspect. They also warn when those logs are older than recent relevant edits under `Assets`, `Packages`, and `ProjectSettings`. Pass `-ChangedPath <path[]>` when verifying a known edit set so generated files outside the task do not make the compile log look stale. Compile-log freshness and runtime console-log freshness are reported separately: stale compiler or batchmode compile logs can fail `-FailOnStale`, while stale `Logs\_console_errors.log` is reported as `runtimeStaleLogNotices` / `isRuntimeLogStale` and does not by itself fail a compile verification.

For automation, pass `-AsJson` to receive a structured result with `ok`, `hasErrors`, `isStale`, error counts, log paths, timestamps, and stale notices. Add `-FailOnStale` to make stale verification a non-zero exit instead of a warning.

When a compiler log is stale or missing, the script prints compiler verification as `not verified`; do not report stale zero-error logs as a successful compile. If Unity MCP `refresh_unity` or another Editor refresh request times out, classify any later zero-error result from stale logs as "last known log state only" and explicitly state that fresh compile verification is still pending.

For missing-script cleanup or asset component migration, run `Find-UnityScriptReferences.ps1` before and after edits. Resolve references by both script name and `.cs.meta` GUID when possible, because Unity serialized assets normally store only the GUID.

## Script Notes

All bundled scripts are PowerShell 7-compatible and use platform-neutral process invocation on Windows and macOS.

The scripts locate the Unity project by walking upward to `ProjectSettings\ProjectVersion.txt`. They can be run from the repository root, the Unity project root, or inside `.agents\skills\unity-debug\scripts`.
