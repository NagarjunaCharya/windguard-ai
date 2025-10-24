# ============================================================================
# WindGuard AI - Git Repository Initialization Script
# ============================================================================
# Description: Initializes local Git repository, connects to GitHub remote,
#              creates phase1-setup branch, and commits initial README
# Usage: .\scripts\git_init.ps1
# ============================================================================

Write-Host "🚀 Initializing WindGuard AI Git Repository..." -ForegroundColor Cyan
Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# Check if Git is installed
Write-Host "📦 Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git from https://git-scm.com/" -ForegroundColor Red
    exit 1
}

# Initialize Git repository if not already initialized
if (-Not (Test-Path ".git")) {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Create .gitignore
Write-Host ""
Write-Host "📝 Creating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
windguard-env/
ENV/
env/
.venv

# PyTorch
*.pth
*.pt
checkpoints/

# Data files
data/raw/*.csv
data/raw/*.fst
data/raw/*.outb
*.h5
*.hdf5

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/

# Node/TypeScript
node_modules/
*.js.map
dist/
.cache/

# Jupyter
.ipynb_checkpoints/

# Temporary files
*.tmp
*.bak
*.backup

# External repositories (optional - uncomment if too large)
# external_repos/

# Documentation downloads
docs/*.pdf
"@
Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "✅ .gitignore created" -ForegroundColor Green

# Check if README exists
if (-Not (Test-Path "README.md")) {
    Write-Host "❌ README.md not found. Please ensure README.md exists." -ForegroundColor Red
    exit 1
}

# Add remote origin
Write-Host ""
Write-Host "🔗 Adding GitHub remote origin..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/NagarjunaCharya/windguard-ai.git"

# Check if remote already exists
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "⚠️  Remote 'origin' already exists: $existingRemote" -ForegroundColor Yellow
    $response = Read-Host "Do you want to update it to $remoteUrl? (y/n)"
    if ($response -eq 'y') {
        git remote set-url origin $remoteUrl
        Write-Host "✅ Remote 'origin' updated" -ForegroundColor Green
    } else {
        Write-Host "⏭️  Keeping existing remote" -ForegroundColor Yellow
    }
} else {
    git remote add origin $remoteUrl
    Write-Host "✅ Remote 'origin' added: $remoteUrl" -ForegroundColor Green
}

# Stage initial files
Write-Host ""
Write-Host "📋 Staging initial files..." -ForegroundColor Yellow
git add README.md
git add .gitignore
git add scripts/
if (Test-Path "backend") { git add backend/ }
if (Test-Path "frontend") { git add frontend/ }
if (Test-Path ".env.example") { git add .env.example }
if (Test-Path "requirements.txt") { git add requirements.txt }

Write-Host "✅ Files staged" -ForegroundColor Green

# Create initial commit on main branch
Write-Host ""
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Project structure and Phase 1 setup scripts

- Add README.md with project overview
- Add Git initialization script
- Add .gitignore for Python, data files, and IDE configs
- Setup project folder structure
- Phase 1: Environment setup and data ingestion pipeline"

Write-Host "✅ Initial commit created" -ForegroundColor Green

# Create and switch to phase1-setup branch
Write-Host ""
Write-Host "🌿 Creating phase1-setup branch..." -ForegroundColor Yellow
git checkout -b phase1-setup 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Switched to phase1-setup branch" -ForegroundColor Green
} else {
    # Branch might already exist
    git checkout phase1-setup
    Write-Host "✅ Switched to existing phase1-setup branch" -ForegroundColor Green
}

# Display status
Write-Host ""
Write-Host "📊 Repository Status:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
git status --short
Write-Host ""
git log --oneline -n 3
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Instructions for pushing
Write-Host ""
Write-Host "✨ Next Steps:" -ForegroundColor Green
Write-Host "1. To push to GitHub, run:" -ForegroundColor White
Write-Host "   git push -u origin phase1-setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Then create main branch:" -ForegroundColor White
Write-Host "   git checkout -b main" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Or push both branches:" -ForegroundColor White
Write-Host "   git push -u origin main phase1-setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Git repository initialization complete!" -ForegroundColor Green
