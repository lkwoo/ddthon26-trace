#Requires -Version 5
<#
.SYNOPSIS
  Uninstaller for knowledge-store (Windows / PowerShell).

.DESCRIPTION
  By default removes the pip package from the local virtual environment.
  Pass -Purge to also delete the .venv directory created by install.ps1.

  Your ingested data (each project's .knowledge-store\ directory) is NEVER
  touched by this script.

.EXAMPLE
  ./uninstall.ps1
  ./uninstall.ps1 -Purge
#>
param(
  [switch]$Purge
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"

if (Test-Path $VenvPy) {
  Write-Host "Uninstalling knowledge-store from $VenvDir ..."
  & $VenvPy -m pip uninstall -y knowledge-store
} else {
  Write-Host "No local .venv found; attempting uninstall with system pip..."
  python -m pip uninstall -y knowledge-store
}

if ($Purge -and (Test-Path $VenvDir)) {
  Write-Host "Removing virtual environment $VenvDir ..."
  Remove-Item -Recurse -Force $VenvDir
}

Write-Host "Done."
Write-Host "Note: ingested data in each project's .knowledge-store\ directory was left untouched."
