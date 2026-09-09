#Requires -Version 5
<#
.SYNOPSIS
  Convenience installer for knowledge-store (Windows / PowerShell).

.DESCRIPTION
  Creates a local virtual environment (.venv) next to this script and installs
  the package into it. Safe to re-run (idempotent).

.PARAMETER Extras
  Optional dependency set to install. One of:
  all (default), mcp, embeddings, vec, code, docs, test, none.

.EXAMPLE
  ./install.ps1
  ./install.ps1 -Extras mcp
  ./install.ps1 -Extras none
#>
param(
  [string]$Extras = "all"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1) locate a Python >= 3.10 interpreter
$python = $null
foreach ($cand in @("python", "py")) {
  if (Get-Command $cand -ErrorAction SilentlyContinue) {
    & $cand -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $python = $cand; break }
  }
}
if (-not $python) {
  Write-Error "Python 3.10+ is required but was not found on PATH."
  exit 1
}
Write-Host "Using Python: $(& $python --version)"

# 2) create the virtual environment (idempotent)
$VenvDir = Join-Path $ScriptDir ".venv"
if (-not (Test-Path $VenvDir)) {
  Write-Host "Creating virtual environment at $VenvDir"
  & $python -m venv $VenvDir
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create the virtual environment (see message above)."
    exit 1
  }
}
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"

# ensure pip is available inside the venv
& $VenvPy -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host "pip not found in the virtual environment; bootstrapping with ensurepip..."
  & $VenvPy -m ensurepip --upgrade | Out-Null
}

# 3) install the package
& $VenvPy -m pip install --upgrade pip | Out-Null
if ($Extras -eq "none") {
  Write-Host "Installing knowledge-store (core only)..."
  & $VenvPy -m pip install .
} else {
  Write-Host "Installing knowledge-store with extra: [$Extras] ..."
  & $VenvPy -m pip install ".[$Extras]"
}

Write-Host ""
Write-Host "Done. knowledge-store is installed in $VenvDir"
Write-Host ""
Write-Host "Run it directly:"
Write-Host "  $VenvDir\Scripts\knowledge-store.exe --help"
Write-Host ""
Write-Host "...or activate the environment first:"
Write-Host "  $VenvDir\Scripts\Activate.ps1"
Write-Host "  knowledge-store install C:\path\to\your\project"
Write-Host "  knowledge-store ingest  C:\path\to\your\project --target C:\path\to\your\project"
