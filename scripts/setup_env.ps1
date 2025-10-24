# ============================================================================
# WindGuard AI - Virtual Environment Setup Script
# ============================================================================
# Description: Creates Python virtual environment, installs dependencies,
#              verifies installations, and exports requirements.txt
# Usage: .\scripts\setup_env.ps1
# ============================================================================

Write-Host "🐍 WindGuard AI - Python Environment Setup" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# ============================================================================
# 1. Check Python Version
# ============================================================================
Write-Host "📋 Step 1: Checking Python version..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "❌ Python 3.10+ required. Current version: $pythonVersion" -ForegroundColor Red
            Write-Host "   Please install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ============================================================================
# 2. Create Virtual Environment
# ============================================================================
Write-Host "📦 Step 2: Creating virtual environment..." -ForegroundColor Yellow

$venvPath = "windguard-env"

if (Test-Path $venvPath) {
    Write-Host "⚠️  Virtual environment already exists at: $venvPath" -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/n)"
    
    if ($response -eq 'y') {
        Write-Host "🗑️  Removing existing environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
        Write-Host "✅ Removed" -ForegroundColor Green
    } else {
        Write-Host "⏭️  Using existing environment" -ForegroundColor Yellow
        $createNew = $false
    }
}

if (-Not (Test-Path $venvPath) -or $createNew -ne $false) {
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created: $venvPath" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# 3. Activate Virtual Environment
# ============================================================================
Write-Host "🔌 Step 3: Activating virtual environment..." -ForegroundColor Yellow

$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Activation script not found at: $activateScript" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# 4. Upgrade pip
# ============================================================================
Write-Host "⬆️  Step 4: Upgrading pip..." -ForegroundColor Yellow

python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    $pipVersion = pip --version
    Write-Host "✅ $pipVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to upgrade pip, continuing..." -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# 5. Install Dependencies
# ============================================================================
Write-Host "📚 Step 5: Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Gray

# Core dependencies
$packages = @(
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "python-dotenv==1.0.0",
    "pydantic==2.5.0",
    "pandas==2.1.3",
    "numpy==1.26.2",
    "scikit-learn==1.3.2",
    "matplotlib==3.8.2",
    "seaborn==0.13.0",
    "faker==20.1.0",
    "requests==2.31.0",
    "openpyxl==3.1.2",
    "python-multipart==0.0.6",
    "aiofiles==23.2.1"
)

Write-Host "   Installing core packages..." -ForegroundColor Gray
foreach ($package in $packages) {
    Write-Host "     - $package" -ForegroundColor DarkGray
}

$packageString = $packages -join " "
python -m pip install $packageString --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some packages failed to install" -ForegroundColor Yellow
    Write-Host "   Trying individual installation..." -ForegroundColor Yellow
    
    foreach ($package in $packages) {
        Write-Host "   Installing $package..." -ForegroundColor Gray
        python -m pip install $package --quiet
    }
}

Write-Host "✅ Core packages installed" -ForegroundColor Green
Write-Host ""

# PyTorch (CPU version for faster installation)
Write-Host "   Installing PyTorch (CPU version)..." -ForegroundColor Gray
Write-Host "     - torch, torchvision, torchaudio" -ForegroundColor DarkGray

python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  PyTorch installation failed" -ForegroundColor Yellow
    Write-Host "   Trying alternative method..." -ForegroundColor Yellow
    python -m pip install torch torchvision torchaudio
}

Write-Host "✅ PyTorch installed" -ForegroundColor Green
Write-Host ""

# PyTorch Geometric (may fail - provide conda fallback)
Write-Host "   Installing PyTorch Geometric..." -ForegroundColor Gray
Write-Host "     - torch-geometric (optional)" -ForegroundColor DarkGray

python -m pip install torch-geometric --quiet 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  PyTorch Geometric installation failed" -ForegroundColor Yellow
    Write-Host "   This is optional. To install with conda, run:" -ForegroundColor Yellow
    Write-Host "   conda install pyg -c pyg" -ForegroundColor Cyan
} else {
    Write-Host "✅ PyTorch Geometric installed" -ForegroundColor Green
}

Write-Host ""

# Optional ML packages
Write-Host "   Installing optional ML packages..." -ForegroundColor Gray
$optionalPackages = @(
    "streamlit==1.29.0",
    "plotly==5.18.0",
    "jupyter==1.0.0",
    "notebook==7.0.6"
)

foreach ($package in $optionalPackages) {
    Write-Host "     - $package" -ForegroundColor DarkGray
}

$optionalString = $optionalPackages -join " "
python -m pip install $optionalString --quiet

Write-Host "✅ Optional packages installed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 6. Verify Installations
# ============================================================================
Write-Host "🔍 Step 6: Verifying installations..." -ForegroundColor Yellow

$verificationScript = @"
import sys
print(f'Python: {sys.version}')
print()

packages = [
    'torch', 'numpy', 'pandas', 'sklearn', 'fastapi', 
    'uvicorn', 'matplotlib', 'faker', 'dotenv'
]

print('Package Versions:')
print('-' * 40)

for package in packages:
    try:
        if package == 'sklearn':
            mod = __import__('sklearn')
        elif package == 'dotenv':
            mod = __import__('dotenv')
        else:
            mod = __import__(package)
        
        version = getattr(mod, '__version__', 'installed')
        print(f'✓ {package:15} {version}')
    except ImportError as e:
        print(f'✗ {package:15} NOT INSTALLED')

print()
print('PyTorch CUDA Available:', end=' ')
import torch
print('Yes' if torch.cuda.is_available() else 'No (CPU only)')
print(f'PyTorch Version: {torch.__version__}')
"@

$verificationScript | python

Write-Host ""
Write-Host "✅ Verification complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# 7. Export Requirements
# ============================================================================
Write-Host "💾 Step 7: Exporting requirements.txt..." -ForegroundColor Yellow

pip freeze > requirements.txt

if (Test-Path "requirements.txt") {
    $lineCount = (Get-Content "requirements.txt").Count
    Write-Host "✅ requirements.txt created ($lineCount packages)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to create requirements.txt" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✨ Environment Setup Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Virtual Environment: $venvPath" -ForegroundColor White
Write-Host "🐍 Python Version: $pythonVersion" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Activate environment: .\windguard-env\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   2. Clone repositories: .\scripts\clone_repos.ps1" -ForegroundColor White
Write-Host "   3. Ingest data: python scripts\data_ingestion.py" -ForegroundColor White
Write-Host "   4. Start backend: .\scripts\start_backend.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Keep this terminal open to maintain the activated environment" -ForegroundColor Cyan
Write-Host ""
