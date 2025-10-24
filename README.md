# WindGuard AI MVP

## 🌀 AI Predictive Maintenance for Envision Wind Turbines

**WindGuard AI** is an advanced predictive maintenance system for wind turbines using BiLSTM neural networks and digital twin technology. The system analyzes real-time sensor data from Envision wind turbines to predict failures, optimize maintenance schedules, and maximize energy output.

## 🎯 Project Overview

- **Objective**: Prevent unplanned downtime in wind turbines through AI-powered anomaly detection
- **Technology**: BiLSTM (Bidirectional Long Short-Term Memory) neural networks with digital twin simulations
- **Data Sources**: EnOS IoT Platform, OpenFAST simulations, SCADA systems
- **Target**: 72-hour predictive maintenance forecasting

## 🏗️ Architecture

### Frontend
- **HTML5** - Structure and semantic markup
- **CSS3** - Responsive design with modern layouts
- **TypeScript** - Type-safe client-side logic

### Backend
- **FastAPI** - High-performance Python web framework
- **PyTorch** - Deep learning model training and inference
- **PostgreSQL** - Time-series data storage
- **Redis** - Real-time data caching

### ML Pipeline
- **BiLSTM Model** - Sequence prediction for anomaly detection
- **Digital Twin** - OpenFAST simulation integration
- **Feature Engineering** - Wind speed, vibration, temperature, yaw analysis

## 📋 Phase 1: Environment Setup & Data Ingestion

### Completed Tasks
✅ Git repository initialization  
✅ Virtual environment setup  
✅ Dependency management  
✅ Data ingestion pipeline  
✅ Mock data generation  
✅ Repository cloning automation  

### Data Sources
1. **EnOS Platform** - Real-time turbine telemetry
2. **PREDICTIVE-MAINTENANCE Repo** - Historical maintenance records
3. **OpenFAST** - Physics-based turbine simulations
4. **Kaggle** - Public wind turbine SCADA datasets
5. **Faker** - Synthetic data for testing

## 🚀 Quick Start

### 1. Initialize Repository
```powershell
.\scripts\git_init.ps1
```

### 2. Setup Environment
```powershell
.\scripts\setup_env.ps1
```

### 3. Ingest Data
```powershell
.\scripts\run_ingestion.ps1
```

### 4. Start Backend
```powershell
.\scripts\start_backend.ps1
```

### 5. Launch Frontend
Open `frontend/index.html` in browser or use Live Server

## 📊 Data Pipeline

```
EnOS IoT → API → Data Ingestion → Preprocessing → Feature Engineering → BiLSTM Model → Predictions → Dashboard
```

## 🔧 Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for TypeScript compilation)
- Git 2.0+
- 8GB RAM minimum

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `ENOS_APP_KEY` - EnOS application key
- `ENOS_APP_SECRET` - EnOS secret
- `ENOS_ORG_ID` - Organization ID
- `DATABASE_URL` - PostgreSQL connection string

## 📁 Project Structure

```
windguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles/
│   └── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
├── scripts/
│   ├── git_init.ps1
│   ├── setup_env.ps1
│   └── data_ingestion.py
├── external_repos/
├── docs/
└── tests/
```

## 🧪 Testing

```powershell
# Run data validation
python scripts/validate_data.py

# Test backend API
pytest tests/

# Check frontend types
tsc --noEmit
```

## 📈 Performance Targets

- **Prediction Accuracy**: >95%
- **False Positive Rate**: <5%
- **Prediction Horizon**: 72 hours
- **API Response Time**: <100ms
- **Data Ingestion**: Real-time streaming

## 🤝 Contributing

This is a hackathon MVP. For production deployment, please review security, scalability, and monitoring requirements.

## 📄 License

MIT License - See LICENSE file

## 👥 Team

Phase 1 - Initial Setup and Data Pipeline  
Built for Envision Wind Turbine Predictive Maintenance Challenge

---

**Status**: Phase 1 Complete ✅  
**Next**: Phase 2 - BiLSTM Model Development
