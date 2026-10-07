[CmdletBinding()]
param([string]$Project)
$ErrorActionPreference = 'Stop'
$shadowPython = if (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' } else { 'python' }
$shadowArguments = @((Join-Path $PSScriptRoot 'shadow_tools.py'), 'pins')
if ($Project) { $shadowArguments += @('--project', $Project) }
& $shadowPython @shadowArguments
exit $LASTEXITCODE
