[CmdletBinding()]
param([string]$Project, [switch]$Apply)
$ErrorActionPreference = 'Stop'
$shadowPython = if (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' } else { 'python' }
$shadowArguments = @((Join-Path $PSScriptRoot 'shadow_tools.py'), 'cache')
if ($Project) { $shadowArguments += @('--project', $Project) }
if ($Apply) { $shadowArguments += '--apply' }
& $shadowPython @shadowArguments
exit $LASTEXITCODE
