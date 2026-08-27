[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string[]]$ScriptName = @(),
    [string[]]$Guid = @(),
    [string[]]$SearchRoot = @("Assets"),
    [string[]]$Extension = @(".prefab", ".unity", ".asset", ".controller", ".overrideController", ".anim", ".mat", ".playable", ".timeline"),
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"

. "$PSScriptRoot\UnityDebug.Common.ps1"

function Get-MetaGuid {
    param([Parameter(Mandatory = $true)][string]$MetaPath)

    if (-not (Test-Path -LiteralPath $MetaPath)) {
        return $null
    }

    $line = Get-Content -Encoding UTF8 -LiteralPath $MetaPath | Where-Object { $_ -match "^\s*guid:\s*([0-9a-fA-F]{32})\s*$" } | Select-Object -First 1
    if (-not $line) {
        return $null
    }

    return ([regex]::Match($line, "^\s*guid:\s*([0-9a-fA-F]{32})\s*$")).Groups[1].Value.ToLowerInvariant()
}

function ConvertTo-RelativeProjectPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd("\")
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if ($fullPath.Equals($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return "."
    }
    if ($fullPath.StartsWith($fullRoot + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath.Substring($fullRoot.Length + 1)
    }
    return $fullPath
}

$resolvedProjectPath = Get-UnityDebugProjectPath -ProjectPath $ProjectPath

$scriptRecords = New-Object System.Collections.Generic.List[object]
$guidSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$nameSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

foreach ($name in $ScriptName) {
    if ([string]::IsNullOrWhiteSpace($name)) { continue }
    foreach ($singleName in ($name -split ",")) {
        if ([string]::IsNullOrWhiteSpace($singleName)) { continue }
        $normalizedName = [System.IO.Path]::GetFileNameWithoutExtension($singleName.Trim())
        [void]$nameSet.Add($normalizedName)

        $matches = Get-ChildItem -LiteralPath (Join-Path $resolvedProjectPath "Assets") -Filter "$normalizedName.cs.meta" -File -Recurse -ErrorAction SilentlyContinue
        foreach ($meta in $matches) {
            $metaGuid = Get-MetaGuid -MetaPath $meta.FullName
            if ($metaGuid) {
                [void]$guidSet.Add($metaGuid)
                [void]$scriptRecords.Add([pscustomobject]@{
                    Name = $normalizedName
                    Guid = $metaGuid
                    MetaPath = ConvertTo-RelativeProjectPath -Root $resolvedProjectPath -Path $meta.FullName
                })
            }
        }
    }
}

foreach ($item in $Guid) {
    if ([string]::IsNullOrWhiteSpace($item)) { continue }
    foreach ($singleGuid in ($item -split ",")) {
        if ([string]::IsNullOrWhiteSpace($singleGuid)) { continue }
        [void]$guidSet.Add($singleGuid.Trim().ToLowerInvariant())
    }
}

if ($guidSet.Count -eq 0 -and $nameSet.Count -eq 0) {
    throw "Provide at least one -ScriptName or -Guid."
}

$roots = foreach ($root in $SearchRoot) {
    if ([string]::IsNullOrWhiteSpace($root)) { continue }
    $candidate = if ([System.IO.Path]::IsPathRooted($root)) { $root } else { Join-Path $resolvedProjectPath $root }
    Resolve-Path -LiteralPath $candidate -ErrorAction SilentlyContinue
}

if (-not $roots) {
    throw "No search roots were found."
}

$extensionSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
$Extension | ForEach-Object { if (-not [string]::IsNullOrWhiteSpace($_)) { [void]$extensionSet.Add($_) } }

$needles = New-Object System.Collections.Generic.List[object]
foreach ($item in $guidSet) {
    [void]$needles.Add([pscustomobject]@{ Type = "guid"; Value = $item })
}
foreach ($item in $nameSet) {
    [void]$needles.Add([pscustomobject]@{ Type = "name"; Value = $item })
}

$results = New-Object System.Collections.Generic.List[object]
$rg = Get-Command "rg.exe" -ErrorAction SilentlyContinue
if (-not $rg) {
    $rg = Get-Command "rg" -ErrorAction SilentlyContinue
}

if ($rg) {
    $globArgs = @()
    foreach ($ext in $extensionSet) {
        $globArgs += "--glob"
        $globArgs += ("*{0}" -f $ext)
    }

    foreach ($needle in $needles) {
        foreach ($root in $roots) {
            $rgOutput = & $rg.Source --line-number --ignore-case --fixed-strings --no-heading @globArgs -- $needle.Value $root.Path 2>$null
            foreach ($line in $rgOutput) {
                if ($line -match "^(.*?):(\d+):(.*)$") {
                    [void]$results.Add([pscustomobject]@{
                        Path = ConvertTo-RelativeProjectPath -Root $resolvedProjectPath -Path $Matches[1]
                        Line = [int]$Matches[2]
                        MatchType = $needle.Type
                        Match = $needle.Value
                        Text = $Matches[3].Trim()
                    })
                }
            }
        }
    }
}
else {
    foreach ($root in $roots) {
        $files = Get-ChildItem -LiteralPath $root.Path -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
            $extensionSet.Contains($_.Extension)
        }

        foreach ($file in $files) {
            $lineNumber = 0
            try {
                foreach ($line in [System.IO.File]::ReadLines($file.FullName)) {
                    $lineNumber++
                    foreach ($needle in $needles) {
                        if ($line.IndexOf($needle.Value, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                            [void]$results.Add([pscustomobject]@{
                                Path = ConvertTo-RelativeProjectPath -Root $resolvedProjectPath -Path $file.FullName
                                Line = $lineNumber
                                MatchType = $needle.Type
                                Match = $needle.Value
                                Text = $line.Trim()
                            })
                        }
                    }
                }
            }
            catch {
                Write-Verbose ("Skipping {0}: {1}" -f $file.FullName, $_.Exception.Message)
            }
        }
    }
}

$output = [pscustomobject]@{
    ProjectPath = $resolvedProjectPath
    Scripts = @($scriptRecords | Sort-Object Name, Guid, MetaPath)
    Guids = @($guidSet | Sort-Object)
    Names = @($nameSet | Sort-Object)
    References = @($results | Sort-Object Path, Line, MatchType, Match)
}

if ($AsJson) {
    $output | ConvertTo-Json -Depth 8
}
else {
    Write-Host ("Project: {0}" -f $output.ProjectPath)
    if ($output.Scripts.Count -gt 0) {
        Write-Host "Resolved script GUIDs:"
        $output.Scripts | Format-Table -AutoSize | Out-String | Write-Host
    }
    else {
        Write-Host "Resolved script GUIDs: none"
    }

    Write-Host ("References: {0}" -f $output.References.Count)
    $output.References | Format-Table Path, Line, MatchType, Match, Text -AutoSize
}
