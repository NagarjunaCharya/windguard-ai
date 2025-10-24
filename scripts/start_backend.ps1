# ============================================================================
# WindGuard AI - Backend Startup Script
# ============================================================================
# Description: Starts the FastAPI backend server
# Usage: .\scripts\start_backend.ps1
# ============================================================================

Write-Host "🚀 Starting WindGuard AI Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Check if virtual environment exists
$venvPath = "windguard-env"
if (-Not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: .\scripts\setup_env.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please configure your settings." -ForegroundColor Green
}

# Check if data exists
$dataPath = "data\processed\combined_data.csv"
if (-Not (Test-Path $dataPath)) {
    Write-Host "⚠️  Processed data not found!" -ForegroundColor Yellow
    Write-Host "   Run: python scripts\data_ingestion.py" -ForegroundColor Cyan
    Write-Host ""
    $response = Read-Host "Do you want to run data ingestion now? (y/n)"
    if ($response -eq 'y') {
        Write-Host "Running data ingestion..." -ForegroundColor Yellow
        python scripts\data_ingestion.py
    }
}

# Start FastAPI server
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🌐 Starting Backend Server..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Server: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "📖 ReDoc: http://localhost:8000/api/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
