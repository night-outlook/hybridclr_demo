[CmdletBinding()]
param(
    [string]$ProjectPath,
    [switch]$Force,
    [switch]$Status,
    [string]$Set,
    [switch]$CheckRunning
)

. "$PSScriptRoot\UnityDebug.Common.ps1"

function Find-UnityInEnvironment {
    $keys = @("UNITY_HOME", "Unity_Home", "UNITY_PATH", "Unity_Path", "UNITY_EDITOR")
    foreach ($key in $keys) {
        $value = [Environment]::GetEnvironmentVariable($key)
        if ([string]::IsNullOrWhiteSpace($value)) {
            continue
        }

        foreach ($candidate in @($value, (Join-Path $value "Unity"), (Join-Path $value "Unity.exe"), (Join-Path $value "Contents/MacOS/Unity"))) {
            $resolved = Resolve-UnityExecutablePath -Path $candidate
            if ($resolved) { return $resolved }
        }
    }

    foreach ($dir in ($env:PATH -split [regex]::Escape([System.IO.Path]::PathSeparator))) {
        if ($dir) {
            foreach ($name in @("Unity", "Unity.exe")) {
                $resolved = Resolve-UnityExecutablePath -Path (Join-Path $dir $name)
                if ($resolved) { return $resolved }
            }
        }
    }

    return $null
}

function Find-UnityInRegistry {
    param([Parameter(Mandatory = $true)][string]$Version)

    if (-not $IsWindows) { return $null }

    $registryPaths = @(
        "HKCU:\Software\Unity Technologies\Unity Hub",
        "HKLM:\SOFTWARE\Unity Technologies\Installers",
        "HKCU:\Software\Unity Technologies\Unity Editor 5.x"
    )

    foreach ($registryPath in $registryPaths) {
        if (-not (Test-Path $registryPath)) {
            continue
        }

        try {
            $items = Get-ChildItem -Path $registryPath -Recurse -ErrorAction SilentlyContinue
            $items += Get-Item -Path $registryPath -ErrorAction SilentlyContinue
            foreach ($item in $items) {
                $properties = Get-ItemProperty -Path $item.PSPath -ErrorAction SilentlyContinue
                foreach ($property in $properties.PSObject.Properties) {
                    $value = [string]$property.Value
                    if ([string]::IsNullOrWhiteSpace($value)) {
                        continue
                    }

                    $direct = if ($value.EndsWith("Unity.exe")) { $value } else { Join-Path $value "Editor\$Version\Editor\Unity.exe" }
                    if (Test-Path -LiteralPath $direct) {
                        return (Resolve-Path -LiteralPath $direct).Path
                    }

                    $editor = Join-Path $value "Editor\Unity.exe"
                    if (Test-Path -LiteralPath $editor) {
                        return (Resolve-Path -LiteralPath $editor).Path
                    }
                }
            }
        }
        catch {
        }
    }

    return $null
}

function Find-UnityInCommonPaths {
    param([Parameter(Mandatory = $true)][string]$Version)

    if (Test-UnityDebugMacOS) {
        foreach ($candidate in @(
            "/Applications/Unity/Hub/Editor/$Version/Unity.app/Contents/MacOS/Unity",
            "/Applications/Unity/Hub/Editor/$Version/Editor/Unity.app/Contents/MacOS/Unity"
        )) {
            $resolved = Resolve-UnityExecutablePath -Path $candidate
            if ($resolved) { return $resolved }
        }
        return $null
    }

    $userProfile = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
    $commonBases = @(
        "C:\Program Files\Unity\Hub\Editor",
        "C:\Program Files\Unity Hub\Editor",
        "D:\Unity\Hub\Editor",
        "E:\Unity\Hub\Editor",
        "C:\Unity\Hub\Editor",
        "D:\Program Files\Unity\Hub\Editor",
        (Join-Path $userProfile "App\Unity")
    )

    foreach ($base in $commonBases) {
        if (-not (Test-Path -LiteralPath $base)) {
            continue
        }

        $exact = Join-Path $base "$Version\Editor\Unity.exe"
        if (Test-Path -LiteralPath $exact) {
            return (Resolve-Path -LiteralPath $exact).Path
        }

        $versionPrefix = ($Version -replace "f\d+$", "")
        foreach ($dir in Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue) {
            if ($dir.Name.Contains($versionPrefix)) {
                $candidate = Join-Path $dir.FullName "Editor\Unity.exe"
                if (Test-Path -LiteralPath $candidate) {
                    return (Resolve-Path -LiteralPath $candidate).Path
                }
            }
        }
    }

    return $null
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath
$version = Get-UnityEditorVersion -ProjectPath $resolvedProjectPath
Save-UnityDebugRepoConfig -ProjectPath $resolvedProjectPath -Version $version

if ($CheckRunning) {
    $running = Test-UnityProjectRunning -ProjectPath $resolvedProjectPath
    Write-Host "Project: $resolvedProjectPath"
    Write-Host ("Unity running for this project: {0}" -f ($(if ($running) { "yes" } else { "no" })))
    exit $(if ($running) { 1 } else { 0 })
}

if ($Status) {
    $running = Test-UnityProjectRunning -ProjectPath $resolvedProjectPath
    $configuredUnity = Get-ConfiguredUnityPath
    Write-Host "Project: $resolvedProjectPath"
    Write-Host "Unity version: $version"
    Write-Host ("Unity running for this project: {0}" -f ($(if ($running) { "yes" } else { "no" })))
    Write-Host ("Configured Unity executable: {0}" -f ($(if ($configuredUnity) { $configuredUnity } else { "not set" })))
    Write-Host "Repo config: $Script:ConfigFile"
    Write-Host "Local config: $Script:LocalConfigFile"
    exit 0
}

if ($Set) {
    $resolvedSet = Resolve-UnityExecutablePath -Path $Set
    if (-not $resolvedSet) {
        Write-Error "Unity executable not found: $Set"
        exit 1
    }
    Save-UnityDebugLocalConfig -UnityPath $resolvedSet
    Write-Host "[OK] Saved Unity executable: $resolvedSet"
    Write-Host "[INFO] Do not commit config.local.json."
    exit 0
}

if (-not $Force) {
    $configuredUnity = Get-ConfiguredUnityPath
    if ($configuredUnity) {
        Write-Host "[OK] Using configured Unity executable: $configuredUnity"
        exit 0
    }
}

Write-Host "[INFO] Searching Unity $version from environment..."
$unityPath = Find-UnityInEnvironment
if (-not $unityPath -and $IsWindows) {
    Write-Host "[INFO] Searching registry..."
    $unityPath = Find-UnityInRegistry -Version $version
}
if (-not $unityPath) {
    Write-Host "[INFO] Searching common install paths..."
    $unityPath = Find-UnityInCommonPaths -Version $version
}

if ($unityPath) {
    Save-UnityDebugLocalConfig -UnityPath $unityPath
    Write-Host "[OK] Found Unity executable: $unityPath"
    exit 0
}

Write-Error "Unity $version was not found. Run Find-Unity.ps1 -Set <Unity executable or Unity.app path>."
exit 1
