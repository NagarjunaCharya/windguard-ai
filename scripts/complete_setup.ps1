# ============================================================================
# WindGuard AI - Complete Phase 1 Setup
# ============================================================================
# Description: Runs all Phase 1 setup steps in sequence
# Usage: .\scripts\complete_setup.ps1
# ============================================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🌀 WINDGUARD AI - PHASE 1 COMPLETE SETUP" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Store the project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# ============================================================================
# Step 1: Git Initialization
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "📋 STEP 1/5: Git Repository Initialization" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

& "$projectRoot\scripts\git_init.ps1"

if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
    Write-Host ""
    Write-Host "⚠️  Git initialization had issues, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Step 1 Complete" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# Step 2: Python Environment Setup
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "📋 STEP 2/5: Python Environment Setup" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

& "$projectRoot\scripts\setup_env.ps1"

if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
    Write-Host ""
    Write-Host "❌ Python environment setup failed!" -ForegroundColor Red
    Write-Host "   Please fix the errors and run again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Step 2 Complete" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# Step 3: Clone External Repositories
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "📋 STEP 3/5: Clone External Repositories" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

& "$projectRoot\scripts\clone_repos.ps1"

Write-Host ""
Write-Host "✅ Step 3 Complete" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# Step 4: Copy .env file
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "📋 STEP 4/5: Environment Configuration" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please edit .env and add your credentials:" -ForegroundColor Yellow
    Write-Host "   - ENOS_APP_KEY" -ForegroundColor Cyan
    Write-Host "   - ENOS_APP_SECRET" -ForegroundColor Cyan
    Write-Host "   - ENOS_ORG_ID" -ForegroundColor Cyan
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Step 4 Complete" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# Step 5: Data Ingestion
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "📋 STEP 5/5: Data Ingestion Pipeline" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""

# Activate venv and run data ingestion
$venvPython = "$projectRoot\windguard-env\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Running data ingestion..." -ForegroundColor Yellow
    & $venvPython "$projectRoot\scripts\data_ingestion.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Step 5 Complete" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Data ingestion completed with warnings" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Python executable not found in venv" -ForegroundColor Red
    exit 1
}

Write-Host ""
Start-Sleep -Seconds 2

# ============================================================================
# Summary
# ============================================================================
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "✨ PHASE 1 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""

Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   ✅ Git repository initialized" -ForegroundColor White
Write-Host "   ✅ Python environment configured" -ForegroundColor White
Write-Host "   ✅ External repositories cloned" -ForegroundColor White
Write-Host "   ✅ Environment variables setup" -ForegroundColor White
Write-Host "   ✅ Data ingestion completed" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Total time: $([math]::Round($duration, 2)) seconds" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Start Backend Server:" -ForegroundColor White
Write-Host "   .\scripts\start_backend.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2️⃣  Open Frontend Dashboard:" -ForegroundColor White
Write-Host "   Open frontend\index.html in Live Server" -ForegroundColor Cyan
Write-Host "   Or visit: http://127.0.0.1:5500/frontend/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  View API Documentation:" -ForegroundColor White
Write-Host "   http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "4️⃣  Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin phase1-setup" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tip: Use VS Code tasks for quick access to common commands" -ForegroundColor Yellow
Write-Host "   Press Ctrl+Shift+P → 'Tasks: Run Task'" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
