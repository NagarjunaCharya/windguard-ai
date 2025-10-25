"""
WindGuard AI - Simplified Flask Backend (No PyTorch Required)
Serves mock predictions for dashboard demonstration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Allow frontend on localhost

print("🚀 WindGuard AI Simplified Backend Ready!")
print("=" * 50)

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'WindGuard AI Backend API (Simplified)',
        'version': '1.0.0-MVP-SIMPLE',
        'endpoints': [
            '/api/turbines',
            '/api/predict/<turbine_id>',
            '/api/metrics',
            '/health'
        ]
    })

@app.route('/api/turbines', methods=['GET'])
def get_turbines():
    """Get all turbine status data"""
    turbines = [
        {
            'id': 1,
            'name': 'Wind Turbine WT-001',
            'status': 'Operational',
            'risk': 23,
            'output': 2.5,
            'location': 'North Sector',
            'last_maintenance': '2025-10-15'
        },
        {
            'id': 2,
            'name': 'Wind Turbine WT-002',
            'status': 'Warning',
            'risk': 65,
            'output': 2.1,
            'location': 'East Sector',
            'last_maintenance': '2025-09-20'
        },
        {
            'id': 3,
            'name': 'Wind Turbine WT-003',
            'status': 'Operational',
            'risk': 18,
            'output': 2.8,
            'location': 'South Sector',
            'last_maintenance': '2025-10-18'
        },
        {
            'id': 4,
            'name': 'Wind Turbine WT-004',
            'status': 'Operational',
            'risk': 32,
            'output': 2.6,
            'location': 'West Sector',
            'last_maintenance': '2025-10-10'
        },
        {
            'id': 5,
            'name': 'Wind Turbine WT-005',
            'status': 'Operational',
            'risk': 15,
            'output': 2.9,
            'location': 'Central Sector',
            'last_maintenance': '2025-10-20'
        }
    ]
    return jsonify(turbines)

@app.route('/api/predict/<int:turbine_id>', methods=['GET'])
def predict(turbine_id):
    """Run ML prediction for given turbine (MOCK DATA)"""
    
    # Mock predictions based on turbine ID
    predictions = {
        1: {'risk': 23.4, 'status': 'OPERATIONAL', 'color': '#10B981'},
        2: {'risk': 65.2, 'status': 'WARNING', 'color': '#F59E0B'},
        3: {'risk': 18.1, 'status': 'OPERATIONAL', 'color': '#10B981'},
        4: {'risk': 32.8, 'status': 'OPERATIONAL', 'color': '#10B981'},
        5: {'risk': 15.5, 'status': 'OPERATIONAL', 'color': '#10B981'},
    }
    
    pred = predictions.get(turbine_id, {'risk': 25.0, 'status': 'OPERATIONAL', 'color': '#10B981'})
    risk_pct = pred['risk']
    status = pred['status']
    color = pred['color']
    
    # Generate forecast
    if risk_pct > 50:
        forecast_values = [
            risk_pct,
            min(100, risk_pct * 1.05),
            min(100, risk_pct * 1.12),
            min(100, risk_pct * 1.15),
            min(100, risk_pct * 1.20),
            min(100, risk_pct * 1.25),
            min(100, risk_pct * 1.30)
        ]
    else:
        forecast_values = [
            risk_pct,
            risk_pct + np.random.uniform(-2, 3),
            risk_pct + np.random.uniform(-1, 4),
            risk_pct + np.random.uniform(-2, 3),
            risk_pct + np.random.uniform(-1, 5),
            risk_pct + np.random.uniform(0, 6),
            risk_pct + np.random.uniform(1, 7)
        ]
        forecast_values = [max(0, min(100, v)) for v in forecast_values]
    
    # Generate explanation
    if risk_pct >= 75:
        explanation = (
            f"⚠️ **High failure risk ({risk_pct:.1f}%)** detected for next 72 hours. "
            f"Primary cause: **Gearbox temperature anomaly** (contributes 53.2% per SHAP analysis). "
            f"Secondary factor: **Vibration levels** (30.8% contribution). "
            f"**Recommendation:** Schedule immediate inspection and prepare for maintenance shutdown."
        )
        action = "Schedule gearbox inspection within 24 hours"
    elif risk_pct >= 50:
        explanation = (
            f"⚠️ **Moderate failure risk ({risk_pct:.1f}%)** detected. "
            f"**Gearbox temperature** trending above normal. "
            f"**Vibration patterns** show minor irregularities. "
            f"**Recommendation:** Monitor closely, schedule maintenance within 5-7 days."
        )
        action = "Schedule inspection within 72 hours, monitor continuously"
    else:
        explanation = (
            f"✓ **Low failure risk ({risk_pct:.1f}%)** - Turbine operating normally. "
            f"All sensor readings within acceptable ranges. "
            f"**Optimization opportunity:** Adjust yaw angle by +15° for 15% performance gain."
        )
        action = "Optimize yaw angle for +15% energy output"
    
    # SHAP feature importance
    feature_importance = {
        'gearbox_temp': 53.2,
        'vibration': 30.8,
        'wind_speed': 10.4,
        'yaw_angle': 5.6
    }
    
    confidence = max(risk_pct, 100 - risk_pct)
    
    return jsonify({
        'turbine_id': turbine_id,
        'risk': round(risk_pct, 2),
        'status': status,
        'gain': 15.0 if risk_pct < 50 else 2.5,
        'explanation': explanation,
        'action': action,
        'color': color,
        'forecast': {
            'hours': ['Now', '+12h', '+24h', '+36h', '+48h', '+60h', '+72h'],
            'risk_values': [round(v, 1) for v in forecast_values]
        },
        'feature_importance': feature_importance,
        'model_confidence': round(confidence, 1),
        'timestamp': pd.Timestamp.now().isoformat()
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get model performance metrics and business impact"""
    return jsonify({
        'model_metrics': {
            'accuracy': 91.27,
            'precision': 84.21,
            'auc_roc': 95.38,
            'recall': 66.67,
            'f1_score': 74.42
        },
        'business_impact': {
            'opex_savings': 520700,
            'savings_percentage': 20,
            'yaw_optimization_gain': 15.0,
            'annual_energy_gain_gwh': 2.8
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'mode': 'simplified',
        'timestamp': pd.Timestamp.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🌬️  WindGuard AI Backend Server (Simplified)")
    print("=" * 50)
    print("📍 Running on: http://localhost:5001")
    print("📖 API Docs: http://localhost:5001/")
    print("=" * 50 + "\n")
    
    try:
        app.run(debug=False, port=5001, host='127.0.0.1', use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")
