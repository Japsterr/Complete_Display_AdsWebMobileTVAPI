<#
run_local_demo.ps1

Opens two PowerShell windows:
 - one for the Django backend (creates venv if needed, migrate, runserver)
 - one for the Vite frontend (installs node deps if needed, runs dev server)

Usage:
  pwsh .\scripts\run_local_demo.ps1

Notes:
 - Requires Python (py) and Node (npm) on PATH.
 - Designed to be run from any location; it detects the repo root relative to this script.
#>

try {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).ProviderPath
} catch {
    Write-Error "Unable to discover repository root. Run this script from the repo or move it to scripts/."
    exit 1
}

Write-Host "Repository root detected: $RepoRoot"

# Ensure virtualenv exists
$venvPath = Join-Path $RepoRoot '.venv'
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath (this may take a moment)..."
    py -3 -m venv $venvPath
}

# Backend command: activate venv, install requirements if missing, migrate, runserver
$backendCmd = @(
    "Set-Location -LiteralPath '$RepoRoot'",
    "& '$venvPath\Scripts\Activate.ps1'",
    "if (-not (Test-Path '.venv')) { Write-Host 'vEnv present' }",
    "py -3 -m pip install -r requirements.txt --upgrade --quiet",
    "py -3 manage.py migrate",
    "py -3 manage.py runserver 0.0.0.0:8000"
) -join "; `n"

Write-Host "Launching backend window..."
Start-Process -FilePath pwsh -ArgumentList '-NoExit', '-Command', $backendCmd

# Frontend command: cd to Workspace, npm install if node_modules doesn't exist, start dev server
$frontendRoot = Join-Path $RepoRoot 'Workspace'
$frontendCmd = @(
    "Set-Location -LiteralPath '$frontendRoot'",
    "if (-not (Test-Path 'node_modules')) { npm install }",
    "npm run dev"
) -join "; `n"

Write-Host "Launching frontend window..."
Start-Process -FilePath pwsh -ArgumentList '-NoExit', '-Command', $frontendCmd

Write-Host "Launched backend and frontend in separate PowerShell windows."
