"""
WindGuard AI - Vercel Serverless API
Lightweight version without PyTorch for Vercel deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/api')
def home():
    return jsonify({
        'message': 'WindGuard AI API',
        'version': '1.0.0-Vercel',
        'endpoints': ['/api/turbines', '/api/predict/<id>', '/api/metrics', '/health']
    })

@app.route('/api/turbines')
def get_turbines():
    turbines = [
        {'id': 1, 'name': 'Wind Turbine WT-001', 'status': 'Operational', 'risk': 23, 'output': 2.5},
        {'id': 2, 'name': 'Wind Turbine WT-002', 'status': 'Warning', 'risk': 65, 'output': 2.1},
        {'id': 3, 'name': 'Wind Turbine WT-003', 'status': 'Operational', 'risk': 18, 'output': 2.8},
        {'id': 4, 'name': 'Wind Turbine WT-004', 'status': 'Operational', 'risk': 32, 'output': 2.6},
        {'id': 5, 'name': 'Wind Turbine WT-005', 'status': 'Operational', 'risk': 15, 'output': 2.9}
    ]
    return jsonify(turbines)

@app.route('/api/predict/<int:turbine_id>')
def predict(turbine_id):
    predictions = {
        1: {'risk': 23.4, 'status': 'OPERATIONAL', 'color': '#10B981'},
        2: {'risk': 65.2, 'status': 'WARNING', 'color': '#F59E0B'},
        3: {'risk': 18.1, 'status': 'OPERATIONAL', 'color': '#10B981'},
        4: {'risk': 32.8, 'status': 'OPERATIONAL', 'color': '#10B981'},
        5: {'risk': 15.5, 'status': 'OPERATIONAL', 'color': '#10B981'}
    }
    
    pred = predictions.get(turbine_id, {'risk': 25.0, 'status': 'OPERATIONAL', 'color': '#10B981'})
    risk_pct = pred['risk']
    
    if risk_pct >= 75:
        explanation = f"⚠️ **High failure risk ({risk_pct:.1f}%)** - Schedule immediate maintenance."
        action = "Schedule gearbox inspection within 24 hours"
    elif risk_pct >= 50:
        explanation = f"⚠️ **Moderate failure risk ({risk_pct:.1f}%)** - Monitor closely."
        action = "Schedule inspection within 72 hours"
    else:
        explanation = f"✓ **Low failure risk ({risk_pct:.1f}%)** - Operating normally."
        action = "Continue routine monitoring"
    
    return jsonify({
        'turbine_id': turbine_id,
        'risk': round(risk_pct, 2),
        'status': pred['status'],
        'gain': 15.0 if risk_pct < 50 else 2.5,
        'explanation': explanation,
        'action': action,
        'color': pred['color'],
        'forecast': {
            'hours': ['Now', '+12h', '+24h', '+36h', '+48h', '+60h', '+72h'],
            'risk_values': [risk_pct, risk_pct+2, risk_pct+5, risk_pct+7, risk_pct+10, risk_pct+12, risk_pct+15]
        },
        'feature_importance': {
            'gearbox_temp': 53.2,
            'vibration': 30.8,
            'wind_speed': 10.4,
            'yaw_angle': 5.6
        },
        'model_confidence': 92.5,
        'timestamp': pd.Timestamp.now().isoformat()
    })

@app.route('/api/metrics')
def get_metrics():
    return jsonify({
        'model_metrics': {
            'accuracy': 91.27,
            'precision': 84.21,
            'auc_roc': 95.38
        },
        'business_impact': {
            'opex_savings': 520700,
            'yaw_optimization_gain': 15.0
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'mode': 'vercel-serverless'})

# Vercel expects this
if __name__ != '__main__':
    # Running on Vercel
    pass
