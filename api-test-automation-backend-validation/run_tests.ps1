$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3.11 -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`nRunning smoke tests..." -ForegroundColor Cyan
pytest -m smoke

Write-Host "`nRunning full suite..." -ForegroundColor Cyan
pytest
