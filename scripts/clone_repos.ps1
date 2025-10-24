# ============================================================================
# WindGuard AI - Repository Cloning Script
# ============================================================================
# Description: Clones external repositories for data and examples
# Usage: .\scripts\clone_repos.ps1
# ============================================================================

Write-Host "📦 WindGuard AI - Cloning External Repositories" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Create external_repos directory
$externalDir = "external_repos"
if (-Not (Test-Path $externalDir)) {
    New-Item -ItemType Directory -Path $externalDir | Out-Null
    Write-Host "✅ Created $externalDir directory" -ForegroundColor Green
}

Set-Location $externalDir

# ============================================================================
# 1. Clone PREDICTIVE-MAINTENANCE Repository
# ============================================================================
Write-Host "📥 Cloning PREDICTIVE-MAINTENANCE repository..." -ForegroundColor Yellow

$repo1 = "PREDICTIVE-MAINTENANCE"
$repo1Url = "https://github.com/umbertogriffo/Predictive-Maintenance-using-LSTM.git"

if (Test-Path $repo1) {
    Write-Host "⚠️  $repo1 already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to pull latest changes? (y/n)"
    if ($response -eq 'y') {
        Set-Location $repo1
        git pull
        Set-Location ..
        Write-Host "✅ Updated $repo1" -ForegroundColor Green
    }
} else {
    Write-Host "   Cloning from: $repo1Url" -ForegroundColor Gray
    git clone $repo1Url $repo1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cloned $repo1" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to clone $repo1" -ForegroundColor Red
    }
}

Write-Host ""

# ============================================================================
# 2. Clone OpenFAST Repository
# ============================================================================
Write-Host "📥 Cloning OpenFAST repository..." -ForegroundColor Yellow

$repo2 = "OpenFAST"
$repo2Url = "https://github.com/OpenFAST/openfast.git"

if (Test-Path $repo2) {
    Write-Host "⚠️  $repo2 already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to pull latest changes? (y/n)"
    if ($response -eq 'y') {
        Set-Location $repo2
        git pull
        Set-Location ..
        Write-Host "✅ Updated $repo2" -ForegroundColor Green
    }
} else {
    Write-Host "   Cloning from: $repo2Url" -ForegroundColor Gray
    Write-Host "   ⚠️  This is a large repository (~500MB), may take several minutes..." -ForegroundColor Yellow
    git clone --depth 1 $repo2Url $repo2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cloned $repo2 (shallow clone)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to clone $repo2" -ForegroundColor Red
    }
}

Write-Host ""

# ============================================================================
# 3. Download Sample Data Files
# ============================================================================
Write-Host "📄 Setting up sample data directories..." -ForegroundColor Yellow

Set-Location $projectRoot

$dataDir = "data"
$rawDir = Join-Path $dataDir "raw"
$processedDir = Join-Path $dataDir "processed"
$modelsDir = Join-Path $dataDir "models"

foreach ($dir in @($dataDir, $rawDir, $processedDir, $modelsDir)) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✅ Created $dir" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================================================
# 4. Copy Sample Files
# ============================================================================
Write-Host "📋 Checking for sample data files..." -ForegroundColor Yellow

$predictiveMaintenancePath = Join-Path $externalDir "PREDICTIVE-MAINTENANCE"
if (Test-Path $predictiveMaintenancePath) {
    $dataFiles = Get-ChildItem -Path $predictiveMaintenancePath -Recurse -Include "*.csv", "*.txt" -ErrorAction SilentlyContinue
    
    if ($dataFiles.Count -gt 0) {
        Write-Host "   Found $($dataFiles.Count) data files" -ForegroundColor Gray
        Write-Host "   Files will be loaded by data_ingestion.py" -ForegroundColor Gray
    } else {
        Write-Host "   No CSV files found (will use mock data)" -ForegroundColor Yellow
    }
}

$openfastPath = Join-Path $externalDir "OpenFAST"
if (Test-Path $openfastPath) {
    $fstFiles = Get-ChildItem -Path $openfastPath -Recurse -Include "*.fst" -ErrorAction SilentlyContinue | Select-Object -First 5
    
    if ($fstFiles.Count -gt 0) {
        Write-Host "   Found $($fstFiles.Count) OpenFAST input files" -ForegroundColor Gray
        Write-Host "   Example: $($fstFiles[0].Name)" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================================================
# 5. Download Documentation (Optional)
# ============================================================================
Write-Host "📚 Documentation Setup" -ForegroundColor Yellow

$docsDir = "docs"
if (-Not (Test-Path $docsDir)) {
    New-Item -ItemType Directory -Path $docsDir | Out-Null
}

Write-Host "   To download EnOS and OpenFAST documentation, visit:" -ForegroundColor Gray
Write-Host "   - EnOS API: https://docs.envisioniot.com/" -ForegroundColor Cyan
Write-Host "   - OpenFAST: https://openfast.readthedocs.io/" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✨ Repository Setup Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# List cloned repositories
Write-Host "📦 Cloned Repositories:" -ForegroundColor White
if (Test-Path (Join-Path $externalDir "PREDICTIVE-MAINTENANCE")) {
    Write-Host "   ✅ PREDICTIVE-MAINTENANCE" -ForegroundColor Green
}
if (Test-Path (Join-Path $externalDir "OpenFAST")) {
    Write-Host "   ✅ OpenFAST" -ForegroundColor Green
}

Write-Host ""
Write-Host "📁 Data Directories:" -ForegroundColor White
Write-Host "   ✅ data/raw/" -ForegroundColor Green
Write-Host "   ✅ data/processed/" -ForegroundColor Green
Write-Host "   ✅ data/models/" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Next Step:" -ForegroundColor Yellow
Write-Host "   Run data ingestion: python scripts\data_ingestion.py" -ForegroundColor White
Write-Host ""
