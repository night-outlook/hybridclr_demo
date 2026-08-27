$ErrorActionPreference = "Stop"

$Script:SkillDir = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$Script:ConfigFile = Join-Path $Script:SkillDir "config.json"
$Script:LocalConfigFile = Join-Path $Script:SkillDir "config.local.json"

function Read-UnityDebugJson {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{}
    }

    $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return [ordered]@{}
    }

    return $raw | ConvertFrom-Json
}

function Write-UnityDebugJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 8
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $encoding)
}

function Resolve-UnityProjectRoot {
    param([string[]]$StartPaths)

    foreach ($startPath in $StartPaths) {
        if ([string]::IsNullOrWhiteSpace($startPath)) {
            continue
        }

        $candidate = Resolve-Path -LiteralPath $startPath -ErrorAction SilentlyContinue
        if (-not $candidate) {
            continue
        }

        $dir = Get-Item -LiteralPath $candidate
        if (-not $dir.PSIsContainer) {
            $dir = $dir.Directory
        }

        while ($dir) {
            $versionFile = Join-Path $dir.FullName "ProjectSettings\ProjectVersion.txt"
            if (Test-Path -LiteralPath $versionFile) {
                return $dir.FullName
            }
            $dir = $dir.Parent
        }
    }

    throw "Unable to locate Unity project root. Expected ProjectSettings\ProjectVersion.txt."
}

function Get-UnityDebugSkillBasePath {
    return (Resolve-Path -LiteralPath (Join-Path $Script:SkillDir "..\..\..")).Path
}

function Test-UnityDebugProjectPath {
    param([string]$Path)

    return -not [string]::IsNullOrWhiteSpace($Path) -and
        (Test-Path -LiteralPath (Join-Path $Path "ProjectSettings\ProjectVersion.txt"))
}

function Resolve-UnityDebugConfiguredProjectPath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }

    if ([System.IO.Path]::IsPathRooted($Path)) {
        $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue).Path
        if (Test-UnityDebugProjectPath $resolved) {
            return $resolved
        }
        return $null
    }

    $directPath = (Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue).Path
    if (Test-UnityDebugProjectPath $directPath) {
        return $directPath
    }

    $skillBasePath = Get-UnityDebugSkillBasePath
    $skillRelativePath = (Resolve-Path -LiteralPath (Join-Path $skillBasePath $Path) -ErrorAction SilentlyContinue).Path
    if (Test-UnityDebugProjectPath $skillRelativePath) {
        return $skillRelativePath
    }

    return $null
}

function Get-UnityDebugProjectPath {
    param([string]$ProjectPath)

    if (-not [string]::IsNullOrWhiteSpace($ProjectPath)) {
        $configuredProjectPath = Resolve-UnityDebugConfiguredProjectPath $ProjectPath
        if ($configuredProjectPath) {
            return $configuredProjectPath
        }
        $root = Resolve-UnityProjectRoot -StartPaths @((Get-Location).Path, $PSScriptRoot)
        return (Resolve-Path -LiteralPath (Join-Path $root $ProjectPath)).Path
    }

    $root = Resolve-UnityProjectRoot -StartPaths @((Get-Location).Path, $PSScriptRoot)

    $config = Read-UnityDebugJson -Path $Script:ConfigFile
    if ($config.project_path) {
        $configuredProjectPath = Resolve-UnityDebugConfiguredProjectPath $config.project_path
        if ($configuredProjectPath) {
            return $configuredProjectPath
        }
        return (Resolve-Path -LiteralPath (Join-Path $root $config.project_path)).Path
    }

    return $root
}

function Get-UnityEditorVersion {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    $versionFile = Join-Path $ProjectPath "ProjectSettings\ProjectVersion.txt"
    if (-not (Test-Path -LiteralPath $versionFile)) {
        throw "ProjectVersion.txt not found: $versionFile"
    }

    $line = Get-Content -Encoding UTF8 -LiteralPath $versionFile | Where-Object { $_ -match "^m_EditorVersion:\s*(\S+)" } | Select-Object -First 1
    if (-not $line) {
        throw "Unable to read m_EditorVersion from $versionFile"
    }

    return ([regex]::Match($line, "^m_EditorVersion:\s*(\S+)")).Groups[1].Value
}

function Save-UnityDebugRepoConfig {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [string]$Version
    )

    $root = Resolve-UnityProjectRoot -StartPaths @($ProjectPath, (Get-Location).Path, $PSScriptRoot)
    $projectFullPath = (Resolve-Path -LiteralPath $ProjectPath).Path
    if (-not $Version) {
        $Version = Get-UnityEditorVersion -ProjectPath $projectFullPath
    }

    $skillBasePath = Get-UnityDebugSkillBasePath
    if ($projectFullPath -eq $skillBasePath) {
        $projectConfigPath = "."
    }
    elseif ($projectFullPath.StartsWith($skillBasePath + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        $projectConfigPath = $projectFullPath.Substring($skillBasePath.Length).TrimStart('\', '/')
    }
    elseif ($projectFullPath -eq $root) {
        $projectConfigPath = "."
    }
    else {
        $projectConfigPath = $projectFullPath
    }
    $existing = Read-UnityDebugJson -Path $Script:ConfigFile
    $hasLocalCompilationField = $null -ne $existing.PSObject.Properties["last_compilation"]
    if ($existing.version -eq $Version -and $existing.project_path -eq $projectConfigPath -and -not $hasLocalCompilationField) {
        return
    }

    $config = [ordered]@{
        version = $Version
        project_path = $projectConfigPath
    }

    Write-UnityDebugJson -Path $Script:ConfigFile -Value $config
}

function Save-UnityDebugLocalConfig {
    param([string]$UnityPath)

    $existing = Read-UnityDebugJson -Path $Script:LocalConfigFile
    $config = [ordered]@{
        unity_path = $existing.unity_path
        last_updated = $existing.last_updated
        last_compilation = $existing.last_compilation
    }

    if ($UnityPath) {
        $resolvedUnityPath = Resolve-UnityExecutablePath -Path $UnityPath
        if (-not $resolvedUnityPath) {
            throw "Unity executable does not exist: $UnityPath"
        }
        $config.unity_path = $resolvedUnityPath
        $config.last_updated = (Get-Date).ToUniversalTime().ToString("o")
    }

    Write-UnityDebugJson -Path $Script:LocalConfigFile -Value $config
}

function Save-UnityDebugLastCompilation {
    $existing = Read-UnityDebugJson -Path $Script:LocalConfigFile
    $config = [ordered]@{
        unity_path = $existing.unity_path
        last_updated = $existing.last_updated
        last_compilation = (Get-Date).ToUniversalTime().ToString("o")
    }

    Write-UnityDebugJson -Path $Script:LocalConfigFile -Value $config
}

function Get-ConfiguredUnityPath {
    $localConfig = Read-UnityDebugJson -Path $Script:LocalConfigFile
    if ($localConfig.unity_path) {
        return Resolve-UnityExecutablePath -Path ([string]$localConfig.unity_path)
    }
    return $null
}

function Test-UnityDebugMacOS {
    return $PSVersionTable.Platform -eq "Unix" -and (uname -s 2>$null) -eq "Darwin"
}

function Resolve-UnityExecutablePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue).Path
    if (-not $resolved) {
        return $null
    }

    if ($resolved.EndsWith(".app", [System.StringComparison]::OrdinalIgnoreCase)) {
        $resolved = Join-Path $resolved "Contents/MacOS/Unity"
    }

    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        return $null
    }
    return (Resolve-Path -LiteralPath $resolved).Path
}

function Format-NativeArgumentList {
    param([string[]]$ArgumentList)

    return (($ArgumentList | ForEach-Object {
        if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ }
    }) -join ' ')
}

function Start-UnityNativeProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [string]$WorkingDirectory,
        [switch]$Hidden
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FilePath
    $startInfo.UseShellExecute = $false
    if ($WorkingDirectory) {
        $startInfo.WorkingDirectory = $WorkingDirectory
    }
    if ($Hidden -and $IsWindows) {
        $startInfo.CreateNoWindow = $true
        $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    }
    foreach ($argument in $ArgumentList) {
        [void]$startInfo.ArgumentList.Add($argument)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "Unity process could not be started."
    }
    return $process
}

function Start-UnityVisibleEditorProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [string]$WorkingDirectory,
        [int]$ResolveTimeoutSec = 30
    )

    if (-not (Test-UnityDebugMacOS)) {
        return Start-UnityNativeProcess -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory
    }

    $appPath = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $FilePath))
    if (-not $appPath.EndsWith(".app", [System.StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $appPath -PathType Container)) {
        throw "The macOS Unity executable is not inside a valid Unity.app bundle: $FilePath"
    }

    $openArguments = @("-n", "-a", $appPath, "--args") + @($ArgumentList)
    $launcher = Start-UnityNativeProcess -FilePath "/usr/bin/open" -ArgumentList $openArguments -WorkingDirectory $WorkingDirectory
    $launcher.WaitForExit()
    if ($launcher.ExitCode -ne 0) {
        throw "macOS LaunchServices could not start Unity (open exit code $($launcher.ExitCode))."
    }

    $deadline = (Get-Date).AddSeconds($ResolveTimeoutSec)
    do {
        $matches = @(Get-UnityProjectProcesses -ProjectPath $ProjectPath)
        if ($matches.Count -gt 1) {
            throw "macOS LaunchServices started an ambiguous set of Unity processes for the exact project."
        }
        if ($matches.Count -eq 1) {
            return [System.Diagnostics.Process]::GetProcessById([int]$matches[0].Id)
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)

    throw "macOS LaunchServices did not expose an exact-project Unity process within $ResolveTimeoutSec seconds."
}

function Get-UnityProjectPathFromCommandLine {
    param([string]$CommandLine)

    if ([string]::IsNullOrWhiteSpace($CommandLine)) {
        return $null
    }
    $match = [regex]::Match($CommandLine, '(?i)(?:^|\s)-projectPath\s+(?:"(?<double>[^"]+)"|''(?<single>[^'']+)''|(?<plain>\S+))')
    if (-not $match.Success) {
        return $null
    }
    $value = @($match.Groups["double"].Value, $match.Groups["single"].Value, $match.Groups["plain"].Value) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Select-Object -First 1
    if (-not $value) {
        return $null
    }
    try { return [System.IO.Path]::GetFullPath($value) } catch { return $null }
}

function Get-UnityEditorProcesses {
    $result = @()
    if ($IsWindows) {
        $rows = @(Get-CimInstance Win32_Process -Filter "name='Unity.exe'" -ErrorAction SilentlyContinue)
        foreach ($row in $rows) {
            $process = Get-Process -Id $row.ProcessId -ErrorAction SilentlyContinue
            $result += [pscustomobject]@{
                Id = [int]$row.ProcessId
                ProjectPath = Get-UnityProjectPathFromCommandLine -CommandLine $row.CommandLine
                WorkingSetBytes = if ($row.WorkingSetSize) { [long]$row.WorkingSetSize } else { 0L }
                StartTime = if ($process) { $process.StartTime } else { $null }
                ExecutablePath = if ($row.ExecutablePath) { [string]$row.ExecutablePath } else { $null }
                IsBatchMode = [bool]($row.CommandLine -match '(?i)(?:^|\s)-batchmode(?:\s|$)')
            }
        }
        return @($result)
    }

    if (Test-UnityDebugMacOS) {
        foreach ($line in @(& /bin/ps -axo pid=,rss=,command= 2>$null)) {
            $match = [regex]::Match([string]$line, '^\s*(?<pid>\d+)\s+(?<rss>\d+)\s+(?<command>.+)$')
            if (-not $match.Success) { continue }
            $commandLine = $match.Groups["command"].Value
            $executableMatch = [regex]::Match($commandLine, '^(?:"(?<quoted>[^"]+)"|(?<plain>\S+))')
            $executablePath = @($executableMatch.Groups["quoted"].Value, $executableMatch.Groups["plain"].Value) | Where-Object { $_ } | Select-Object -First 1
            if (-not $executablePath -or $executablePath -notmatch '/Unity\.app/Contents/MacOS/Unity$') { continue }
            $process = Get-Process -Id ([int]$match.Groups["pid"].Value) -ErrorAction SilentlyContinue
            $result += [pscustomobject]@{
                Id = [int]$match.Groups["pid"].Value
                ProjectPath = Get-UnityProjectPathFromCommandLine -CommandLine $commandLine
                WorkingSetBytes = [long]$match.Groups["rss"].Value * 1KB
                StartTime = if ($process) { $process.StartTime } else { $null }
                ExecutablePath = $executablePath
                IsBatchMode = [bool]($commandLine -match '(?i)(?:^|\s)-batchmode(?:\s|$)')
            }
        }
    }
    return @($result)
}

function Test-UnityPathEqual {
    param([string]$Left, [string]$Right)

    if ([string]::IsNullOrWhiteSpace($Left) -or [string]::IsNullOrWhiteSpace($Right)) { return $false }
    try {
        $leftFull = [System.IO.Path]::TrimEndingDirectorySeparator([System.IO.Path]::GetFullPath($Left))
        $rightFull = [System.IO.Path]::TrimEndingDirectorySeparator([System.IO.Path]::GetFullPath($Right))
        $comparison = if ($IsWindows) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
        return $leftFull.Equals($rightFull, $comparison)
    }
    catch { return $false }
}

function Get-UnityProjectIdentityHash {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    $resolvedProject = [System.IO.Path]::GetFullPath($ProjectPath).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar)
    $dataPath = ($resolvedProject.Replace('\', '/') + "/Assets")
    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($dataPath)
        $hash = $sha1.ComputeHash($bytes)
        return ([System.BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant()).Substring(0, 16)
    }
    finally {
        $sha1.Dispose()
    }
}

function Get-UnityMcpProjectInstances {
    param(
        $Instances,
        [Parameter(Mandatory = $true)][string]$ProjectPath
    )

    if (-not $Instances -or -not $Instances.instances) { return @() }
    $expectedHash = Get-UnityProjectIdentityHash -ProjectPath $ProjectPath
    return @($Instances.instances | Where-Object {
        $pathMatches = $_.project_path -and (Test-UnityPathEqual $_.project_path $ProjectPath)
        $reportedHash = @($_.hash, $_.project_hash) |
            Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
            Select-Object -First 1
        $hashMatches = $reportedHash -and [string]::Equals(
            [string]$reportedHash,
            $expectedHash,
            [System.StringComparison]::OrdinalIgnoreCase)
        $idMatches = $_.id -and ([string]$_.id).EndsWith(
            "@$expectedHash",
            [System.StringComparison]::OrdinalIgnoreCase)
        $pathMatches -or $hashMatches -or $idMatches
    })
}

function Get-UnityDebugSha256 {
    param([Parameter(Mandatory = $true)][string]$Text)

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return [System.BitConverter]::ToString($sha256.ComputeHash($bytes)).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha256.Dispose()
    }
}

function ConvertTo-UnityDebugUtcDateTime {
    param($Value)

    if ($Value -is [datetime]) {
        return ([datetime]$Value).ToUniversalTime()
    }
    if ([string]::IsNullOrWhiteSpace([string]$Value)) { return $null }

    $parsed = [datetime]::MinValue
    $parsedOk = [datetime]::TryParse(
        [string]$Value,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::RoundtripKind,
        [ref]$parsed)
    if (-not $parsedOk) { return $null }
    return $parsed.ToUniversalTime()
}

function Get-UnityDebugProcessCommandLine {
    param([Parameter(Mandatory = $true)][int]$ProcessId)

    try {
        if ($IsWindows) {
            $row = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction Stop
            return [string]$row.CommandLine
        }
        $psPath = if (Test-Path -LiteralPath "/bin/ps") { "/bin/ps" } else { "ps" }
        return ((& $psPath -p $ProcessId -ww -o command= 2>$null | Out-String).Trim())
    }
    catch {
        return $null
    }
}

function Get-UnityDebugListeningProcessIds {
    param([Parameter(Mandatory = $true)][int]$Port)

    $ids = @()
    try {
        if ($IsWindows) {
            $connections = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop)
            $ids = @($connections | ForEach-Object { [int]$_.OwningProcess })
        }
        else {
            $lsofPath = if (Test-Path -LiteralPath "/usr/sbin/lsof") { "/usr/sbin/lsof" } else { "lsof" }
            $ids = @(& $lsofPath -nP "-iTCP:$Port" -sTCP:LISTEN -t 2>$null |
                Where-Object { [string]$_ -match '^\d+$' } |
                ForEach-Object { [int]$_ })
        }
    }
    catch {
        return @()
    }
    return @($ids | Sort-Object -Unique)
}

function Get-UnityMcpServerPidFilePath {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [int]$Port = 8080
    )

    return Join-Path ([System.IO.Path]::GetFullPath($ProjectPath)) "Library/MCPForUnity/RunState/mcp_http_$Port.pid"
}

function Test-UnityMcpServerCommandLine {
    param(
        [string]$CommandLine,
        [Parameter(Mandatory = $true)][string]$PidFilePath
    )

    if ([string]::IsNullOrWhiteSpace($CommandLine)) { return $false }
    $compact = ($CommandLine -replace '\s', '').ToLowerInvariant()
    $pidFileCompact = ([System.IO.Path]::GetFullPath($PidFilePath) -replace '\s', '').ToLowerInvariant()
    $mentionsServer = $compact.Contains("mcp-for-unity") -or
        $compact.Contains("mcp_for_unity") -or
        $compact.Contains("mcpforunityserver")
    return $mentionsServer -and
        $compact.Contains("--transport") -and
        $compact.Contains("http") -and
        $compact.Contains("--pidfile") -and
        $compact.Contains($pidFileCompact) -and
        $compact.Contains("--unity-instance-token")
}

function Get-UnityMcpServerOwnershipRecord {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [int]$Port = 8080,
        [int[]]$PreexistingProcessIds = @(),
        [datetime]$NotBeforeUtc
    )

    try {
        $pidFilePath = Get-UnityMcpServerPidFilePath -ProjectPath $ProjectPath -Port $Port
        if (-not (Test-Path -LiteralPath $pidFilePath -PathType Leaf)) { return $null }
        $pidText = (Get-Content -Raw -Encoding UTF8 -LiteralPath $pidFilePath).Trim()
        $serverPid = 0
        if (-not [int]::TryParse($pidText, [ref]$serverPid) -or $serverPid -le 0) { return $null }
        if ($PreexistingProcessIds -contains $serverPid) { return $null }

        $listeners = @(Get-UnityDebugListeningProcessIds -Port $Port)
        if ($listeners.Count -ne 1 -or $listeners[0] -ne $serverPid) { return $null }
        $process = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
        if (-not $process) { return $null }
        $processStartUtc = $process.StartTime.ToUniversalTime()
        if ($NotBeforeUtc -and $processStartUtc -lt $NotBeforeUtc.ToUniversalTime().AddSeconds(-2)) { return $null }

        $commandLine = Get-UnityDebugProcessCommandLine -ProcessId $serverPid
        if (-not (Test-UnityMcpServerCommandLine -CommandLine $commandLine -PidFilePath $pidFilePath)) { return $null }

        return [pscustomobject]@{
            schemaVersion = 1
            owner = "agent-unity-launch"
            pid = $serverPid
            port = $Port
            projectPath = [System.IO.Path]::GetFullPath($ProjectPath)
            pidFilePath = [System.IO.Path]::GetFullPath($pidFilePath)
            processStartTimeUtc = $processStartUtc.ToString("o")
            commandLineSha256 = Get-UnityDebugSha256 -Text $commandLine
        }
    }
    catch {
        return $null
    }
}

function Stop-UnityMcpServerFromOwnershipRecord {
    param(
        [Parameter(Mandatory = $true)]$Record,
        [int]$TimeoutSec = 15,
        [switch]$DryRun
    )

    $blockers = @()
    $schemaVersion = 0
    $serverPid = 0
    $port = 0
    if (-not [int]::TryParse([string]$Record.schemaVersion, [ref]$schemaVersion) -or
        $schemaVersion -ne 1 -or [string]$Record.owner -ne "agent-unity-launch") {
        $blockers += "MCP server record does not identify an agent-owned launch."
    }
    if (-not [int]::TryParse([string]$Record.pid, [ref]$serverPid) -or $serverPid -le 0) {
        $blockers += "MCP server record has an invalid PID."
    }
    if (-not [int]::TryParse([string]$Record.port, [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
        $blockers += "MCP server record has an invalid port."
    }
    $expectedPidFile = $null
    if ($Record.projectPath -and $port -gt 0) {
        try { $expectedPidFile = Get-UnityMcpServerPidFilePath -ProjectPath ([string]$Record.projectPath) -Port $port }
        catch { $blockers += "MCP server record has an invalid project path." }
    }
    if (-not $expectedPidFile -or -not (Test-UnityPathEqual $expectedPidFile ([string]$Record.pidFilePath))) {
        $blockers += "MCP server pidfile is outside the recorded project's run-state path."
    }

    $recordedStart = ConvertTo-UnityDebugUtcDateTime -Value $Record.processStartTimeUtc
    if (-not $recordedStart) {
        $blockers += "MCP server record has an invalid process start time."
    }
    if ([string]::IsNullOrWhiteSpace([string]$Record.commandLineSha256) -or
        [string]$Record.commandLineSha256 -notmatch '^[0-9a-fA-F]{64}$') {
        $blockers += "MCP server record has an invalid command fingerprint."
    }
    if ($blockers.Count -gt 0) {
        return [pscustomobject]@{ ok = $false; dryRun = [bool]$DryRun; alreadyStopped = $false; pid = $(if ($serverPid -gt 0) { $serverPid } else { $null }); blockers = @($blockers) }
    }

    $process = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
    $listeners = @(Get-UnityDebugListeningProcessIds -Port $port)
    if (-not $process -and $listeners -notcontains $serverPid) {
        if ($blockers.Count -gt 0) {
            return [pscustomobject]@{ ok = $false; dryRun = [bool]$DryRun; alreadyStopped = $true; pid = $serverPid; blockers = @($blockers) }
        }
        if ($expectedPidFile -and (Test-Path -LiteralPath $expectedPidFile -PathType Leaf)) {
            $stalePid = (Get-Content -Raw -Encoding UTF8 -LiteralPath $expectedPidFile).Trim()
            if ($stalePid -eq [string]$serverPid -and -not $DryRun) {
                Remove-Item -LiteralPath $expectedPidFile -Force
            }
        }
        return [pscustomobject]@{ ok = $true; dryRun = [bool]$DryRun; alreadyStopped = $true; pid = $serverPid; blockers = @() }
    }

    if (-not $process) { $blockers += "Recorded MCP server PID is not running, but its port ownership is ambiguous." }
    elseif ($listeners.Count -ne 1 -or $listeners[0] -ne $serverPid) { $blockers += "Recorded MCP server PID is not the sole listener on its port." }
    else {
        if ([math]::Abs(($process.StartTime.ToUniversalTime() - $recordedStart).TotalSeconds) -gt 2) {
            $blockers += "Recorded MCP server PID start time no longer matches."
        }
        $commandLine = Get-UnityDebugProcessCommandLine -ProcessId $serverPid
        if (-not (Test-UnityMcpServerCommandLine -CommandLine $commandLine -PidFilePath $expectedPidFile)) {
            $blockers += "Recorded MCP server PID no longer matches the server command contract."
        }
        elseif (-not [string]::Equals(
            (Get-UnityDebugSha256 -Text $commandLine),
            [string]$Record.commandLineSha256,
            [System.StringComparison]::OrdinalIgnoreCase)) {
            $blockers += "Recorded MCP server command fingerprint no longer matches."
        }
        if (-not (Test-Path -LiteralPath $expectedPidFile -PathType Leaf) -or
            (Get-Content -Raw -Encoding UTF8 -LiteralPath $expectedPidFile).Trim() -ne [string]$serverPid) {
            $blockers += "Recorded MCP server pidfile no longer names the listener PID."
        }
    }

    if ($blockers.Count -gt 0) {
        return [pscustomobject]@{ ok = $false; dryRun = [bool]$DryRun; alreadyStopped = $false; pid = $serverPid; blockers = @($blockers) }
    }
    if ($DryRun) {
        return [pscustomobject]@{ ok = $true; dryRun = $true; alreadyStopped = $false; pid = $serverPid; blockers = @() }
    }

    Stop-Process -Id $serverPid -ErrorAction Stop
    try {
        Wait-Process -Id $serverPid -Timeout $TimeoutSec -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{ ok = $false; dryRun = $false; alreadyStopped = $false; pid = $serverPid; blockers = @("The recorded MCP server did not exit within $TimeoutSec seconds; no forced termination was attempted.") }
    }
    if (Test-Path -LiteralPath $expectedPidFile -PathType Leaf) {
        $remainingPid = (Get-Content -Raw -Encoding UTF8 -LiteralPath $expectedPidFile).Trim()
        if ($remainingPid -eq [string]$serverPid) { Remove-Item -LiteralPath $expectedPidFile -Force }
    }
    return [pscustomobject]@{ ok = $true; dryRun = $false; alreadyStopped = $false; pid = $serverPid; blockers = @() }
}

function Get-UnityProjectProcesses {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    return @(Get-UnityEditorProcesses | Where-Object { Test-UnityPathEqual $_.ProjectPath $ProjectPath })
}

function Get-UnityAvailableMemory {
    try {
        if ($IsWindows) {
            $operatingSystem = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
            return [pscustomobject]@{ Succeeded = $true; AvailableGB = [math]::Round(($operatingSystem.FreePhysicalMemory * 1KB) / 1GB, 2); Source = "Win32_OperatingSystem" }
        }
        if (Test-UnityDebugMacOS) {
            $totalBytes = [long](& /usr/sbin/sysctl -n hw.memsize 2>$null)
            $pressure = (& /usr/bin/memory_pressure -Q 2>$null | Out-String)
            $match = [regex]::Match($pressure, 'System-wide memory free percentage:\s*(?<percent>\d+)%')
            if ($totalBytes -le 0 -or -not $match.Success) { throw "macOS memory tools returned incomplete data." }
            $availableBytes = $totalBytes * ([double]$match.Groups["percent"].Value / 100.0)
            return [pscustomobject]@{ Succeeded = $true; AvailableGB = [math]::Round($availableBytes / 1GB, 2); Source = "memory_pressure" }
        }
    }
    catch {
        return [pscustomobject]@{ Succeeded = $false; AvailableGB = $null; Source = "unavailable"; Error = $_.Exception.Message }
    }
    return [pscustomobject]@{ Succeeded = $false; AvailableGB = $null; Source = "unsupported"; Error = "Unsupported operating system." }
}

function Test-UnityEditorMemoryGate {
    param(
        [Parameter(Mandatory = $true)]$Memory,
        [Parameter(Mandatory = $true)][int]$OtherEditorCount,
        [double]$MinimumAvailableMemoryGB = 4
    )

    if (-not $Memory.Succeeded) {
        return [pscustomobject]@{ Allowed = $false; Reason = "Available-memory probe failed."; RequiredGB = $(if ($OtherEditorCount -gt 0) { $MinimumAvailableMemoryGB } else { $null }) }
    }
    if ($OtherEditorCount -gt 0 -and [double]$Memory.AvailableGB -lt $MinimumAvailableMemoryGB) {
        return [pscustomobject]@{ Allowed = $false; Reason = "Another Unity Editor is running and available memory is below the required threshold."; RequiredGB = $MinimumAvailableMemoryGB }
    }
    return [pscustomobject]@{ Allowed = $true; Reason = $(if ($OtherEditorCount -gt 0) { "Other Editors exist and the memory threshold passed." } else { "No other Unity Editor exists; memory was measured without a fixed threshold." }); RequiredGB = $(if ($OtherEditorCount -gt 0) { $MinimumAvailableMemoryGB } else { $null }) }
}

function Test-UnityStartupReadinessState {
    param(
        [Parameter(Mandatory = $true)][bool]$ProcessAlive,
        [Parameter(Mandatory = $true)][bool]$ExactProjectOwned,
        [Parameter(Mandatory = $true)][bool]$HasAutomationReadyEvidence,
        [double]$EvidenceStableSeconds = 0,
        [double]$RequiredStableSeconds = 10
    )

    return $ProcessAlive -and $ExactProjectOwned -and $HasAutomationReadyEvidence -and
        $EvidenceStableSeconds -ge $RequiredStableSeconds
}

function Get-UnityWindowEvidenceKind {
    param(
        [string[]]$Titles,
        [Parameter(Mandatory = $true)][string]$ProjectPath
    )

    $projectWindowFound = $false
    foreach ($title in @($Titles)) {
        if ([string]::IsNullOrWhiteSpace($title)) { continue }
        if ([string]$title -match '(?i)Enter Safe Mode|Safe Mode') { return "safe-mode-window" }
        if (([string]$title).Contains($ProjectPath)) { $projectWindowFound = $true }
    }
    if ($projectWindowFound) { return "project-window" }
    return $null
}

function Get-UnityVisibleEditorLaunchPermission {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $configPath = Join-Path $RepositoryRoot ".agents\config\config.json"
    try {
        $config = Read-UnityDebugJson -Path $configPath
        $allowed = Test-UnityVisibleEditorLaunchPermissionValue -Config $config
        return [pscustomobject]@{ Allowed = $allowed; Source = "RepositoryConfig"; ConfigPath = $configPath }
    }
    catch {
        return [pscustomobject]@{ Allowed = $false; Source = "FailClosed"; ConfigPath = $configPath; Error = $_.Exception.Message }
    }
}

function Test-UnityVisibleEditorLaunchPermissionValue {
    param($Config)

    if ($null -eq $Config -or $Config -isnot [pscustomobject]) { return $false }
    $section = $Config.PSObject.Properties["unity_debug"]
    $property = if ($section -and $section.Value -is [pscustomobject]) { $section.Value.PSObject.Properties["allow_agent_to_launch_visible_editor"] } else { $null }
    return $null -ne $property -and $property.Value -is [bool] -and $property.Value
}

function Test-UnityProjectRunning {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    $projectFullPath = (Resolve-Path -LiteralPath $ProjectPath).Path
    $lockFile = Join-Path $projectFullPath "Temp\UnityLockfile"
    if (Test-Path -LiteralPath $lockFile) {
        try {
            $stream = [System.IO.File]::Open($lockFile, "Open", "ReadWrite", "None")
            $stream.Close()
        }
        catch {
            return $true
        }
    }

    return @(Get-UnityProjectProcesses -ProjectPath $projectFullPath).Count -gt 0
}

function Get-UnityLaunchSourceSnapshot {
    param([Parameter(Mandatory = $true)][string]$Root)

    $excludedNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    @(".git", "Library", "Temp", "Logs", "_temp", "obj", "bin", "BuildInfo") |
        ForEach-Object { [void]$excludedNames.Add($_) }
    $includedExtensions = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    @(".cs", ".asmdef", ".asmref") | ForEach-Object { [void]$includedExtensions.Add($_) }
    $includedNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    @("manifest.json", "packages-lock.json", "ProjectVersion.txt") | ForEach-Object { [void]$includedNames.Add($_) }
    $directories = [System.Collections.Generic.Stack[System.IO.DirectoryInfo]]::new()
    $directories.Push([System.IO.DirectoryInfo]::new([System.IO.Path]::GetFullPath($Root)))
    $latest = $null

    while ($directories.Count -gt 0) {
        $directory = $directories.Pop()
        try {
            foreach ($childPath in [System.IO.Directory]::EnumerateDirectories($directory.FullName)) {
                $child = [System.IO.DirectoryInfo]::new($childPath)
                if (-not $excludedNames.Contains($child.Name)) { $directories.Push($child) }
            }
            foreach ($filePath in [System.IO.Directory]::EnumerateFiles($directory.FullName)) {
                $file = [System.IO.FileInfo]::new($filePath)
                if (-not $includedExtensions.Contains($file.Extension) -and -not $includedNames.Contains($file.Name)) { continue }
                if (-not $latest -or $file.LastWriteTimeUtc -gt $latest.LastWriteTimeUtc) { $latest = $file }
            }
        }
        catch {
            Write-Verbose ("Skipping launch-source snapshot path {0}: {1}" -f $directory.FullName, $_.Exception.Message)
        }
    }

    return [pscustomobject]@{
        Path = if ($latest) { $latest.FullName } else { $null }
        LastWriteTimeUtc = if ($latest) { $latest.LastWriteTimeUtc } else { $null }
    }
}

function Format-UnityDebugTimestamp {
    param($Timestamp)

    if ($null -eq $Timestamp) {
        return "missing"
    }

    return ([datetime]$Timestamp).ToString("yyyy-MM-dd HH:mm:ss K")
}

function Get-UnityDebugLogTimestamp {
    param([string]$Path)

    if ($Path -and (Test-Path -LiteralPath $Path)) {
        return (Get-Item -LiteralPath $Path).LastWriteTime
    }

    return $null
}

function Get-UnityDebugRecentEdit {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [string[]]$ChangedPath
    )

    if ($ChangedPath -and $ChangedPath.Count -gt 0) {
        $latestFile = $null
        $latestTime = $null

        foreach ($path in $ChangedPath) {
            if ([string]::IsNullOrWhiteSpace($path)) {
                continue
            }

            $candidatePath = if ([System.IO.Path]::IsPathRooted($path)) {
                $path
            }
            else {
                Join-Path $ProjectPath $path
            }

            $resolved = Resolve-Path -LiteralPath $candidatePath -ErrorAction SilentlyContinue
            if (-not $resolved) {
                continue
            }

            $item = Get-Item -LiteralPath $resolved.Path
            $files = if ($item.PSIsContainer) {
                Get-ChildItem -LiteralPath $item.FullName -File -Recurse -ErrorAction SilentlyContinue
            }
            else {
                @($item)
            }

            foreach ($file in $files) {
                if ($null -eq $latestTime -or $file.LastWriteTime -gt $latestTime) {
                    $latestFile = $file.FullName
                    $latestTime = $file.LastWriteTime
                }
            }
        }

        return [pscustomobject]@{
            Path = $latestFile
            LastWriteTime = $latestTime
        }
    }

    $relativeRoots = @(
        "Assets",
        "Packages",
        "ProjectSettings"
    )
    $excludedDirNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    @(
        ".git",
        "Library",
        "Temp",
        "Logs",
        "_temp",
        "obj",
        "bin",
        "Build",
        "Builds",
        "Generated",
        "gen"
    ) | ForEach-Object { [void]$excludedDirNames.Add($_) }
    $includedExtensions = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    @(
        ".cs",
        ".asmdef",
        ".asmref",
        ".asset",
        ".prefab",
        ".unity",
        ".mat",
        ".controller",
        ".overrideController",
        ".anim",
        ".shader",
        ".cginc",
        ".hlsl",
        ".compute",
        ".json",
        ".xml",
        ".txt",
        ".bytes",
        ".csv",
        ".lua",
        ".uxml",
        ".uss"
    ) | ForEach-Object { [void]$includedExtensions.Add($_) }

    $latestFile = $null
    $latestTime = $null
    $dirs = New-Object System.Collections.Generic.Stack[System.IO.DirectoryInfo]

    foreach ($relativeRoot in $relativeRoots) {
        $root = Join-Path $ProjectPath $relativeRoot
        if (Test-Path -LiteralPath $root) {
            $dirs.Push((Get-Item -LiteralPath $root))
        }
    }

    while ($dirs.Count -gt 0) {
        $dir = $dirs.Pop()
        if ($excludedDirNames.Contains($dir.Name)) {
            continue
        }

        try {
            foreach ($childDir in [System.IO.Directory]::EnumerateDirectories($dir.FullName)) {
                $childDirInfo = [System.IO.DirectoryInfo]::new($childDir)
                if (-not $excludedDirNames.Contains($childDirInfo.Name)) {
                    $dirs.Push($childDirInfo)
                }
            }

            foreach ($file in [System.IO.Directory]::EnumerateFiles($dir.FullName)) {
                $fileInfo = [System.IO.FileInfo]::new($file)
                if (-not $includedExtensions.Contains($fileInfo.Extension)) {
                    continue
                }
                if ($null -eq $latestTime -or $fileInfo.LastWriteTime -gt $latestTime) {
                    $latestFile = $fileInfo.FullName
                    $latestTime = $fileInfo.LastWriteTime
                }
            }
        }
        catch {
            Write-Verbose ("Skipping recent edit scan path {0}: {1}" -f $dir.FullName, $_.Exception.Message)
        }
    }

    return [pscustomobject]@{
        Path = $latestFile
        LastWriteTime = $latestTime
    }
}

function Get-UnityDebugStaleLogNotices {
    param(
        [Parameter(Mandatory = $true)]$RecentEdit,
        [array]$Logs
    )

    $notices = @()
    if (-not $RecentEdit -or -not $RecentEdit.LastWriteTime) {
        return @($notices)
    }

    foreach ($log in $Logs) {
        if (-not $log.Path -or -not $log.LastWriteTime) {
            continue
        }
        if ($log.LastWriteTime -lt $RecentEdit.LastWriteTime) {
            $notices += ("[WARN] {0} is older than recent relevant edit: {1} ({2})." -f $log.Label, $RecentEdit.Path, (Format-UnityDebugTimestamp -Timestamp $RecentEdit.LastWriteTime))
        }
    }

    return @($notices)
}

function Get-UnityDebugActionableConsoleErrorCount {
    param(
        [array]$ConsoleErrors,
        [array]$RuntimeStaleLogNotices
    )

    if (@($RuntimeStaleLogNotices).Count -gt 0) {
        return 0
    }

    return @($ConsoleErrors).Count
}

function Get-UnityDebugReproMarker {
    param([Parameter(Mandatory = $true)][string]$ProjectPath)

    $markerPath = Join-Path $ProjectPath "_temp\UnityDebug_ReproMarker.json"
    if (-not (Test-Path -LiteralPath $markerPath)) {
        return $null
    }

    try {
        $marker = Read-UnityDebugJson -Path $markerPath
        $startedAt = $null
        if ($marker.local_started_at) {
            $startedAt = [datetime]$marker.local_started_at
        }
        elseif ($marker.started_at) {
            $startedAt = ([datetime]$marker.started_at).ToLocalTime()
        }

        return [pscustomobject]@{
            Path = $markerPath
            StartedAt = $startedAt
        }
    }
    catch {
        Write-Verbose ("Unable to read Unity repro marker {0}: {1}" -f $markerPath, $_.Exception.Message)
        return $null
    }
}

function Get-UnityDebugIgnoredConsoleErrorReason {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line)) {
        return $null
    }

    if ($Line -match 'McpManagerClientHub Version handshake failed' -or
        $Line -match 'MCP-FOR-UNITY' -or
        $Line -match 'MCPForUnity\.Editor' -or
        $Line -match 'com\.IvanMurzak\.McpPlugin\.McpManagerClientHub' -or
        $Line -match 'com\.IvanMurzak\.Unity\.MCP') {
        return "Unity MCP handshake noise"
    }

    return $null
}

function Get-UnityDebugErrorLines {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectPath,
        [switch]$IncludeEditorCompilerLog,
        [switch]$IncludeBatchmodeCompileLog,
        [string[]]$ChangedPath
    )

    $compilerLog = Join-Path $ProjectPath "Logs\_compiler_errors.log"
    $consoleLog = Join-Path $ProjectPath "Logs\_console_errors.log"
    $tempDir = Join-Path $ProjectPath "_temp"

    $compilerErrors = @()
    $consoleErrors = @()
    $ignoredConsoleErrors = @()
    $batchmodeErrors = @()
    $batchmodeLog = $null
    $recentEdit = Get-UnityDebugRecentEdit -ProjectPath $ProjectPath -ChangedPath $ChangedPath
    $reproMarker = Get-UnityDebugReproMarker -ProjectPath $ProjectPath

    if ($IncludeEditorCompilerLog -and (Test-Path -LiteralPath $compilerLog)) {
        $compilerErrors = Get-Content -Encoding UTF8 -LiteralPath $compilerLog | ForEach-Object { $_.Trim().TrimStart([char]0xFEFF) } | Where-Object { $_ }
    }
    if (Test-Path -LiteralPath $consoleLog) {
        $rawConsoleErrors = Get-Content -Encoding UTF8 -LiteralPath $consoleLog | ForEach-Object { $_.Trim().TrimStart([char]0xFEFF) } | Where-Object { $_ }
        foreach ($line in $rawConsoleErrors) {
            $ignoredReason = Get-UnityDebugIgnoredConsoleErrorReason -Line $line
            if ($ignoredReason) {
                $ignoredConsoleErrors += [pscustomobject]@{
                    Reason = $ignoredReason
                    Line = $line
                }
            }
            else {
                $consoleErrors += $line
            }
        }
    }
    if ($IncludeBatchmodeCompileLog -and (Test-Path -LiteralPath $tempDir)) {
        $latestCompileLog = Get-ChildItem -LiteralPath $tempDir -Filter "UnityCompile_*.log" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestCompileLog) {
            $batchmodeLog = $latestCompileLog.FullName
            $seen = [System.Collections.Generic.HashSet[string]]::new()
            Get-Content -Encoding UTF8 -LiteralPath $latestCompileLog.FullName | ForEach-Object {
                $line = $_.Trim().TrimStart([char]0xFEFF)
                if ($line -match "error CS\d+:" -and $seen.Add($line)) {
                    $batchmodeErrors += $line
                }
            }
        }
    }

    $compilerLogLastWriteTime = Get-UnityDebugLogTimestamp -Path $compilerLog
    $consoleLogLastWriteTime = Get-UnityDebugLogTimestamp -Path $consoleLog
    $batchmodeLogLastWriteTime = Get-UnityDebugLogTimestamp -Path $batchmodeLog
    $staleLogNotices = Get-UnityDebugStaleLogNotices -RecentEdit $recentEdit -Logs @(
        [pscustomobject]@{ Label = "Logs\_compiler_errors.log"; Path = $(if ($IncludeEditorCompilerLog) { $compilerLog } else { $null }); LastWriteTime = $compilerLogLastWriteTime },
        [pscustomobject]@{ Label = "batchmode compile log"; Path = $batchmodeLog; LastWriteTime = $batchmodeLogLastWriteTime }
    )
    $runtimeStaleLogNotices = Get-UnityDebugStaleLogNotices -RecentEdit $recentEdit -Logs @(
        [pscustomobject]@{ Label = "Logs\_console_errors.log"; Path = $consoleLog; LastWriteTime = $consoleLogLastWriteTime }
    )
    if ($reproMarker -and $reproMarker.StartedAt -and $consoleLogLastWriteTime -and $consoleLogLastWriteTime -lt $reproMarker.StartedAt) {
        $runtimeStaleLogNotices += ("[WARN] Logs\_console_errors.log is older than repro marker: {0}." -f (Format-UnityDebugTimestamp -Timestamp $reproMarker.StartedAt))
    }

    $editorCompilerVerification = $null
    if ($IncludeEditorCompilerLog) {
        if (-not $compilerLogLastWriteTime) {
            $editorCompilerVerification = "not verified - Logs\_compiler_errors.log is missing or has no timestamp."
        }
        elseif ($recentEdit.LastWriteTime -and $compilerLogLastWriteTime -lt $recentEdit.LastWriteTime) {
            $editorCompilerVerification = "not verified - Logs\_compiler_errors.log is older than recent relevant edit."
        }
    }

    $batchmodeCompileVerification = $null
    if ($IncludeBatchmodeCompileLog) {
        if (-not $batchmodeLogLastWriteTime) {
            $batchmodeCompileVerification = "not verified - no batchmode compile log was found."
        }
        elseif ($recentEdit.LastWriteTime -and $batchmodeLogLastWriteTime -lt $recentEdit.LastWriteTime) {
            $batchmodeCompileVerification = "not verified - batchmode compile log is older than recent relevant edit."
        }
    }

    return [pscustomobject]@{
        CompilerLog = $(if ($IncludeEditorCompilerLog) { $compilerLog } else { $null })
        ConsoleLog = $consoleLog
        BatchmodeLog = $batchmodeLog
        ShowBatchmodeCompileLog = [bool]$IncludeBatchmodeCompileLog
        CompilerLogLastWriteTime = $compilerLogLastWriteTime
        ConsoleLogLastWriteTime = $consoleLogLastWriteTime
        BatchmodeLogLastWriteTime = $batchmodeLogLastWriteTime
        RecentRelevantEditPath = $recentEdit.Path
        RecentRelevantEditLastWriteTime = $recentEdit.LastWriteTime
        ReproMarkerPath = $(if ($reproMarker) { $reproMarker.Path } else { $null })
        ReproMarkerStartedAt = $(if ($reproMarker) { $reproMarker.StartedAt } else { $null })
        StaleLogNotices = @($staleLogNotices)
        RuntimeStaleLogNotices = @($runtimeStaleLogNotices)
        EditorCompilerVerification = $editorCompilerVerification
        BatchmodeCompileVerification = $batchmodeCompileVerification
        CompilerErrors = @($compilerErrors)
        ConsoleErrors = @($consoleErrors)
        IgnoredConsoleErrors = @($ignoredConsoleErrors)
        BatchmodeErrors = @($batchmodeErrors)
    }
}

function Write-UnityDebugErrors {
    param([Parameter(Mandatory = $true)]$Errors)

    if ($Errors.CompilerLog) {
        Write-Host ("Editor log compiler errors (Logs\_compiler_errors.log): {0}" -f $Errors.CompilerErrors.Count)
        Write-Host ("Editor compiler log timestamp: {0}" -f (Format-UnityDebugTimestamp -Timestamp $Errors.CompilerLogLastWriteTime))
        if ($Errors.EditorCompilerVerification) {
            Write-Host ("Editor compiler verification: {0}" -f $Errors.EditorCompilerVerification)
        }
    }
    if ($Errors.CompilerLog -and $Errors.CompilerErrors.Count -gt 0) {
        Write-Host ""
        Write-Host "=== Editor Log Compiler Errors ==="
        $Errors.CompilerErrors | ForEach-Object { Write-Host $_ }
        Write-Host ""
    }

    if ($Errors.ShowBatchmodeCompileLog) {
        Write-Host ("Batchmode compile errors: {0}" -f $Errors.BatchmodeErrors.Count)
        if ($Errors.BatchmodeLog) {
            Write-Host ("Batchmode log: {0}" -f $Errors.BatchmodeLog)
        }
        Write-Host ("Batchmode log timestamp: {0}" -f (Format-UnityDebugTimestamp -Timestamp $Errors.BatchmodeLogLastWriteTime))
        if ($Errors.BatchmodeCompileVerification) {
            Write-Host ("Batchmode compile verification: {0}" -f $Errors.BatchmodeCompileVerification)
        }
        if ($Errors.BatchmodeErrors.Count -gt 0) {
            Write-Host ""
            Write-Host "=== Batchmode Compile Errors ==="
            $Errors.BatchmodeErrors | ForEach-Object { Write-Host $_ }
        }
        Write-Host ""
    }

    Write-Host ("Console errors: {0}" -f $Errors.ConsoleErrors.Count)
    Write-Host ("Console log timestamp: {0}" -f (Format-UnityDebugTimestamp -Timestamp $Errors.ConsoleLogLastWriteTime))
    if ($Errors.IgnoredConsoleErrors.Count -gt 0) {
        Write-Host ("Ignored console noise: {0}" -f $Errors.IgnoredConsoleErrors.Count)
        $Errors.IgnoredConsoleErrors | Group-Object Reason | ForEach-Object {
            Write-Host ("  {0}: {1}" -f $_.Name, $_.Count)
        }
    }
    if ($Errors.ReproMarkerStartedAt) {
        Write-Host ("Repro marker: {0} ({1})" -f $Errors.ReproMarkerPath, (Format-UnityDebugTimestamp -Timestamp $Errors.ReproMarkerStartedAt))
    }
    if ($Errors.RecentRelevantEditLastWriteTime) {
        Write-Host ("Recent relevant edit: {0} ({1})" -f $Errors.RecentRelevantEditPath, (Format-UnityDebugTimestamp -Timestamp $Errors.RecentRelevantEditLastWriteTime))
    }
    if ($Errors.StaleLogNotices.Count -gt 0) {
        Write-Host ""
        $Errors.StaleLogNotices | ForEach-Object { Write-Host $_ }
    }
    if ($Errors.RuntimeStaleLogNotices.Count -gt 0) {
        Write-Host ""
        $Errors.RuntimeStaleLogNotices | ForEach-Object { Write-Host $_ }
    }
    if ($Errors.ConsoleErrors.Count -gt 0) {
        Write-Host ""
        Write-Host "=== Console Errors ==="
        $Errors.ConsoleErrors | ForEach-Object { Write-Host $_ }
    }
}
