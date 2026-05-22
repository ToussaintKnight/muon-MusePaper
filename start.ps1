# Muse one-click startup — launches uvicorn and opens your browser
$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# ── Check if port 8000 is already in use ─────────────────────────────
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "`n⚠️  Port 8000 is already in use." -ForegroundColor Yellow
    Write-Host "   Opening http://localhost:8000 in your browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:8000"
    exit 0
}

# ── Activate Conda (base env at S:\Miniconda) ─────────────────────────
$condaExe = "S:\Miniconda\Scripts\conda.exe"
if (Test-Path $condaExe) {
    (& $condaExe "shell.powershell" "hook") | Out-String | Invoke-Expression
    conda activate base | Out-Null
} else {
    Write-Host "⚠️  Conda not found at $condaExe — assuming dependencies are on PATH" -ForegroundColor Yellow
}

# ── Start Uvicorn ────────────────────────────────────────────────────
Write-Host "`n🚀 Starting Muse on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop`n" -ForegroundColor DarkGray

# Open browser after a short delay so the server is ready
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000"
} | Out-Null

# Run uvicorn in foreground so logs are visible and Ctrl+C works
uvicorn main:app --host 0.0.0.0 --port 8000
