param([Parameter(Mandatory = $true)][string]$ProjectPath)
$ErrorActionPreference = 'Stop'
$project = [System.IO.Path]::GetFullPath($ProjectPath)
$helper = Join-Path $project '.agents/skills/unity-debug/scripts/UnityDebug.Common.ps1'
if (-not (Test-Path -LiteralPath $helper -PathType Leaf)) { throw 'The shared exact-project Unity detection helper is required.' }
. $helper
if (Test-UnityProjectRunning -ProjectPath $project) { Write-Error 'The exact Unity project is already running. No process was stopped.'; exit 2 }
exit 0
