# 🚀 WindGuard AI - Quick Start Guide

## 📋 Phase 1 Setup Checklist

### Prerequisites
- ✅ Python 3.10+ installed
- ✅ Git installed
- ✅ VS Code with Live Server extension (optional)
- ✅ 8GB RAM minimum

---

## 🎯 Option 1: Complete Automated Setup (Recommended)

Run the complete setup script that handles everything:

```powershell
.\scripts\complete_setup.ps1
```

This will:
1. ✅ Initialize Git repository
2. ✅ Create Python virtual environment
3. ✅ Install all dependencies
4. ✅ Clone external repositories
5. ✅ Run data ingestion pipeline

**Time:** ~5-10 minutes depending on internet speed

---

## 🔧 Option 2: Step-by-Step Setup

### Step 1: Initialize Git Repository

```powershell
.\scripts\git_init.ps1
```

Creates Git repo, adds remote, creates phase1-setup branch.

### Step 2: Create Python Environment

```powershell
.\scripts\setup_env.ps1
```

Creates venv, installs dependencies, verifies installation.

**Important:** Keep the terminal open after this step to maintain the activated environment!

### Step 3: Clone External Repositories

```powershell
.\scripts\clone_repos.ps1
```

Clones PREDICTIVE-MAINTENANCE and OpenFAST repositories.

### Step 4: Configure Environment Variables

```powershell
# Copy template
Copy-Item .env.example .env

# Edit .env and add your credentials
notepad .env
```

Add your EnOS credentials:
- `ENOS_APP_KEY`
- `ENOS_APP_SECRET`
- `ENOS_ORG_ID`

### Step 5: Run Data Ingestion

```powershell
python scripts\data_ingestion.py
```

Generates mock data, processes it, and saves to `data/processed/`

---

## 🚀 Running the Application

### Start Backend Server

```powershell
.\scripts\start_backend.ps1
```

Backend will run at: **http://localhost:8000**

API Docs: **http://localhost:8000/api/docs**

### Open Frontend Dashboard

**Option A: Using Live Server (Recommended)**
1. Install "Live Server" extension in VS Code
2. Right-click `frontend/index.html`
3. Select "Open with Live Server"

**Option B: Directly in Browser**
```powershell
# Open in default browser
Start-Process "file:///c:/Users/Nagarjuna/OneDrive/Desktop/CYPHER_3.02/frontend/index.html"
```

---

## 📁 Project Structure

```
windguard-ai/
├── 📄 README.md                 # Project overview
├── 📄 QUICKSTART.md            # This file
├── 📄 requirements.txt         # Python dependencies
├── 📄 .env.example             # Environment template
│
├── 📂 scripts/                 # Setup & utility scripts
│   ├── git_init.ps1           # Git initialization
│   ├── setup_env.ps1          # Environment setup
│   ├── clone_repos.ps1        # Clone external repos
│   ├── complete_setup.ps1     # Complete automated setup
│   ├── start_backend.ps1      # Start FastAPI server
│   └── data_ingestion.py      # Data pipeline
│
├── 📂 backend/                 # FastAPI backend
│   └── app/
│       ├── main.py            # Main application
│       ├── models/            # Data models
│       ├── routes/            # API endpoints
│       └── services/          # Business logic
│
├── 📂 frontend/                # Web dashboard
│   ├── index.html             # Main page
│   ├── styles/
│   │   └── main.css           # Styling
│   └── scripts/
│       └── main.ts            # TypeScript app
│
├── 📂 data/                    # Data storage
│   ├── raw/                   # Raw data files
│   ├── processed/             # Processed datasets
│   └── models/                # ML model files
│
├── 📂 external_repos/          # Cloned repositories
│   ├── PREDICTIVE-MAINTENANCE/
│   └── OpenFAST/
│
└── 📂 .vscode/                 # VS Code configuration
    └── tasks.json             # Automated tasks
```

---

## 🎮 VS Code Tasks (Quick Commands)

Press `Ctrl+Shift+P` → `Tasks: Run Task` → Select:

- **🔄 Full Setup: Complete Phase 1** - Run entire setup
- **🚀 Backend: Start FastAPI Server** - Start backend
- **📊 Data: Run Data Ingestion** - Regenerate data
- **🔧 Setup: Initialize Git Repository** - Git init only
- **🐍 Setup: Create Python Environment** - Venv only

---

## 🧪 Testing the Installation

### 1. Check Python Environment

```powershell
.\windguard-env\Scripts\Activate.ps1
python -c "import torch, pandas, fastapi; print('✅ All packages OK')"
```

### 2. Verify Data Generation

```powershell
# Check processed data exists
Test-Path data\processed\combined_data.csv

# View data summary
python -c "import pandas as pd; df = pd.read_csv('data/processed/combined_data.csv'); print(df.info())"
```

### 3. Test Backend API

```powershell
# In another terminal, after starting backend
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/data/summary
```

---

## ❓ Troubleshooting

### Issue: "Python not found"
**Solution:**
```powershell
# Check Python installation
python --version

# If not found, download from python.org
Start-Process "https://www.python.org/downloads/"
```

### Issue: "Virtual environment activation fails"
**Solution:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\windguard-env\Scripts\Activate.ps1
```

### Issue: "PyTorch installation fails"
**Solution:**
```powershell
# Install CPU-only version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "Backend won't start"
**Solution:**
```powershell
# Check if data exists
python scripts\data_ingestion.py

# Check if .env exists
Copy-Item .env.example .env

# Try starting again
.\scripts\start_backend.ps1
```

### Issue: "Port 8000 already in use"
**Solution:**
```powershell
# Find and kill process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Or change port in .env
# PORT=8001
```

---

## 📊 Verify Phase 1 Completion

✅ **Checklist:**

- [ ] Git repository initialized
- [ ] Remote origin added: `https://github.com/NagarjunaCharya/windguard-ai.git`
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (check `pip list`)
- [ ] External repos cloned to `external_repos/`
- [ ] Data ingestion completed successfully
- [ ] `data/processed/` contains CSV files
- [ ] Backend starts without errors
- [ ] API docs accessible at `/api/docs`
- [ ] Frontend loads in browser
- [ ] Dashboard displays turbine cards

---

## 🎯 Next Steps After Phase 1

### Phase 2: BiLSTM Model Development
```powershell
# Create model training script
python scripts/train_bilstm.py

# Features to implement:
# - Time series sequence preparation
# - BiLSTM architecture (2 layers, 128 units)
# - Training loop with validation
# - Model checkpointing
# - Prediction inference
```

### Phase 3: Digital Twin Integration
- Integrate OpenFAST simulation
- Real-time data streaming from EnOS
- Advanced analytics dashboard

---

## 📚 Documentation & Resources

- **API Documentation:** http://localhost:8000/api/docs
- **EnOS Platform:** https://docs.envisioniot.com/
- **OpenFAST:** https://openfast.readthedocs.io/
- **FastAPI:** https://fastapi.tiangolo.com/
- **PyTorch:** https://pytorch.org/docs/

---

## 🤝 Git Workflow

### Commit Phase 1 Work

```powershell
# Add all files
git add .

# Commit
git commit -m "Phase 1 complete: Environment setup and data ingestion"

# Push to GitHub
git push -u origin phase1-setup

# Create main branch
git checkout -b main
git push -u origin main
```

---

## 💡 Pro Tips

1. **Keep terminal open** after activating venv to maintain environment
2. **Use VS Code tasks** for quick access to common commands
3. **Check logs** in `data_ingestion.log` if data pipeline fails
4. **Monitor backend** in terminal to see API requests in real-time
5. **Use API docs** at `/api/docs` to test endpoints interactively

---

## 🎉 Success Indicators

You've successfully completed Phase 1 if:

1. ✅ Backend responds at `http://localhost:8000/health`
2. ✅ API returns data summary with turbine information
3. ✅ Frontend displays 4 turbine cards with health status
4. ✅ Charts render with time-series data
5. ✅ Predict button triggers API call and shows results

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review terminal output for error messages
3. Verify all prerequisites are installed
4. Check file permissions and paths
5. Ensure ports 8000 and 5500 are available

---

**Built with ❤️ for Envision Wind Turbine Challenge**

Phase 1 Status: ✅ Complete
