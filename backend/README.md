# WindGuard AI - Backend Module

This directory contains the FastAPI backend application.

## Structure

```
backend/
├── app/
│   ├── __init__.py      # Application initialization
│   ├── main.py          # Main FastAPI application
│   ├── models/          # Pydantic models (schemas)
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
```

## Running the Backend

```powershell
# Using the startup script
.\scripts\start_backend.ps1

# Or directly with uvicorn
python -m uvicorn backend.app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
