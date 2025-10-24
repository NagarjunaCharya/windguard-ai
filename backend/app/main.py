"""
============================================================================
WindGuard AI - FastAPI Backend Main Application
============================================================================
Description: High-performance REST API for wind turbine predictive
             maintenance system. Serves ML predictions, real-time data,
             and digital twin simulations.

Features:
- RESTful API endpoints
- Real-time data streaming
- ML model inference
- Anomaly detection
- Digital twin integration
- CORS support
- Auto-generated API documentation

Usage: uvicorn backend.app.main:app --reload
============================================================================
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import services (will be created)
# from .services import prediction_service, data_service, alert_service

# ============================================================================
# Configuration
# ============================================================================
class Settings:
    """Application settings from environment variables"""
    APP_NAME: str = os.getenv("APP_NAME", "WindGuard AI")
    VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:5500"
    ).split(",")
    
    # Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
    MODELS_DIR: Path = Path(os.getenv("MODELS_DIR", "data/models"))

settings = Settings()

# ============================================================================
# Logging Setup
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================
class TurbineData(BaseModel):
    """Wind turbine sensor reading"""
    turbine_id: str = Field(..., description="Turbine identifier")
    timestamp: datetime = Field(..., description="Measurement timestamp")
    wind_speed: float = Field(..., ge=0, le=50, description="Wind speed in m/s")
    vibration: float = Field(..., ge=0, description="Vibration in mm/s")
    gearbox_temperature: float = Field(..., description="Temperature in Celsius")
    yaw_position: float = Field(..., ge=0, lt=360, description="Yaw angle in degrees")
    rotor_speed: float = Field(..., ge=0, description="Rotor speed in RPM")
    power_output: float = Field(..., ge=0, description="Power output in kW")

    class Config:
        json_schema_extra = {
            "example": {
                "turbine_id": "WT001",
                "timestamp": "2024-01-15T10:30:00",
                "wind_speed": 12.5,
                "vibration": 1.8,
                "gearbox_temperature": 55.3,
                "yaw_position": 245.0,
                "rotor_speed": 10.2,
                "power_output": 1850.5
            }
        }

class PredictionRequest(BaseModel):
    """Request for failure prediction"""
    turbine_id: str
    prediction_horizon_hours: int = Field(default=72, ge=1, le=168)
    include_confidence: bool = True

class PredictionResponse(BaseModel):
    """Prediction result"""
    turbine_id: str
    prediction_time: datetime
    failure_probability: float = Field(..., ge=0, le=1)
    risk_level: str = Field(..., description="low, medium, high, critical")
    predicted_failure_time: Optional[datetime] = None
    confidence: Optional[float] = None
    anomaly_score: float
    recommendations: List[str]

class HealthStatus(BaseModel):
    """Turbine health status"""
    turbine_id: str
    status: str = Field(..., description="healthy, warning, critical, offline")
    overall_health_score: float = Field(..., ge=0, le=100)
    last_updated: datetime
    active_alerts: int
    metrics: Dict[str, float]

class DataSummary(BaseModel):
    """Data ingestion summary"""
    total_records: int
    date_range_start: datetime
    date_range_end: datetime
    anomaly_count: int
    anomaly_rate: float
    turbines_monitored: List[str]

# ============================================================================
# FastAPI Application
# ============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered predictive maintenance for wind turbines using BiLSTM and digital twins",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# CORS Middleware
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Startup/Shutdown Events
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    
    # Check if data directories exist
    if not settings.PROCESSED_DIR.exists():
        logger.warning(f"Processed data directory not found: {settings.PROCESSED_DIR}")
        logger.info("Run data ingestion: python scripts/data_ingestion.py")
    
    # Load ML model (when available)
    # await prediction_service.load_model()
    
    logger.info("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")
    # Close database connections, save states, etc.

# ============================================================================
# API Routes
# ============================================================================

# --- Health & Status ---
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "docs": "/api/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "database": "not_configured",
            "ml_model": "not_loaded",
            "data_ingestion": "ready"
        }
    }

# --- Data Endpoints ---
@app.get("/api/v1/data/summary", response_model=DataSummary, tags=["Data"])
async def get_data_summary():
    """Get summary of ingested data"""
    try:
        import pandas as pd
        
        data_path = settings.PROCESSED_DIR / "combined_data.csv"
        
        if not data_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Data not found. Run data ingestion first."
            )
        
        df = pd.read_csv(data_path)
        
        return DataSummary(
            total_records=len(df),
            date_range_start=pd.to_datetime(df['timestamp'].min()),
            date_range_end=pd.to_datetime(df['timestamp'].max()),
            anomaly_count=int(df['is_anomaly'].sum()),
            anomaly_rate=float(df['is_anomaly'].mean()),
            turbines_monitored=df['turbine_id'].unique().tolist()
        )
        
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/data/turbine/{turbine_id}", tags=["Data"])
async def get_turbine_data(
    turbine_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Get recent data for a specific turbine"""
    try:
        import pandas as pd
        
        data_path = settings.PROCESSED_DIR / "combined_data.csv"
        df = pd.read_csv(data_path)
        
        turbine_data = df[df['turbine_id'] == turbine_id]
        
        if len(turbine_data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for turbine {turbine_id}"
            )
        
        # Get recent records
        turbine_data = turbine_data.sort_values('timestamp', ascending=False)
        paginated = turbine_data.iloc[offset:offset+limit]
        
        return {
            "turbine_id": turbine_id,
            "total_records": len(turbine_data),
            "returned_records": len(paginated),
            "data": paginated.to_dict('records')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting turbine data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Prediction Endpoints ---
@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_failure(request: PredictionRequest):
    """Predict potential failures for a turbine"""
    try:
        # Placeholder for ML model prediction
        # In production, this would call the trained BiLSTM model
        
        import random
        
        failure_prob = random.uniform(0.1, 0.9)
        
        if failure_prob < 0.3:
            risk_level = "low"
        elif failure_prob < 0.6:
            risk_level = "medium"
        elif failure_prob < 0.8:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        recommendations = []
        if risk_level in ["high", "critical"]:
            recommendations.append("Schedule immediate inspection")
            recommendations.append("Monitor vibration levels closely")
        elif risk_level == "medium":
            recommendations.append("Plan maintenance within 7 days")
        else:
            recommendations.append("Continue normal operation")
        
        predicted_failure = None
        if failure_prob > 0.7:
            predicted_failure = datetime.now() + timedelta(hours=request.prediction_horizon_hours * (1 - failure_prob))
        
        return PredictionResponse(
            turbine_id=request.turbine_id,
            prediction_time=datetime.now(),
            failure_probability=failure_prob,
            risk_level=risk_level,
            predicted_failure_time=predicted_failure,
            confidence=0.85 if request.include_confidence else None,
            anomaly_score=failure_prob * 100,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health-status/{turbine_id}", response_model=HealthStatus, tags=["Health"])
async def get_health_status(turbine_id: str):
    """Get current health status of a turbine"""
    try:
        import pandas as pd
        import random
        
        data_path = settings.PROCESSED_DIR / "combined_data.csv"
        df = pd.read_csv(data_path)
        
        turbine_data = df[df['turbine_id'] == turbine_id].tail(1)
        
        if len(turbine_data) == 0:
            raise HTTPException(status_code=404, detail=f"Turbine {turbine_id} not found")
        
        # Calculate health score
        health_score = random.uniform(60, 95)
        
        if health_score > 85:
            status = "healthy"
        elif health_score > 70:
            status = "warning"
        elif health_score > 50:
            status = "critical"
        else:
            status = "offline"
        
        return HealthStatus(
            turbine_id=turbine_id,
            status=status,
            overall_health_score=health_score,
            last_updated=datetime.now(),
            active_alerts=random.randint(0, 3),
            metrics={
                "vibration_health": random.uniform(70, 100),
                "temperature_health": random.uniform(70, 100),
                "power_efficiency": random.uniform(80, 100),
                "uptime_percentage": random.uniform(85, 99)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Ingest Data ---
@app.post("/api/v1/data/ingest", status_code=status.HTTP_201_CREATED, tags=["Data"])
async def ingest_sensor_data(data: TurbineData, background_tasks: BackgroundTasks):
    """Ingest new sensor reading (real-time stream)"""
    try:
        # In production, this would:
        # 1. Validate data
        # 2. Store in database
        # 3. Trigger anomaly detection
        # 4. Queue for model prediction
        
        logger.info(f"Received data for turbine {data.turbine_id}")
        
        # Simulate background processing
        # background_tasks.add_task(process_sensor_data, data)
        
        return {
            "status": "accepted",
            "message": "Data queued for processing",
            "turbine_id": data.turbine_id,
            "timestamp": data.timestamp
        }
        
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Analytics ---
@app.get("/api/v1/analytics/anomalies", tags=["Analytics"])
async def get_anomalies(
    turbine_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50
):
    """Get detected anomalies"""
    try:
        import pandas as pd
        
        data_path = settings.PROCESSED_DIR / "combined_data.csv"
        df = pd.read_csv(data_path)
        
        # Filter anomalies
        anomalies = df[df['is_anomaly'] == 1]
        
        if turbine_id:
            anomalies = anomalies[anomalies['turbine_id'] == turbine_id]
        
        if start_date:
            anomalies = anomalies[pd.to_datetime(anomalies['timestamp']) >= start_date]
        
        if end_date:
            anomalies = anomalies[pd.to_datetime(anomalies['timestamp']) <= end_date]
        
        anomalies = anomalies.sort_values('timestamp', ascending=False).head(limit)
        
        return {
            "total_anomalies": len(anomalies),
            "anomalies": anomalies.to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error fetching anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Error Handlers
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# Run Application
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
