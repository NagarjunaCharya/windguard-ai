"""
============================================================================
WindGuard AI - Phase 2: End-to-End Verification Script
============================================================================
Description: Comprehensive verification script to test the entire ML pipeline
             end-to-end. Validates model performance, tests prediction function,
             and prepares artifacts for Phase 3 dashboard integration.

Features:
- Load and verify all Phase 2 artifacts (model, scaler, sequences)
- Run full evaluation to confirm targets (accuracy >85%, precision >80%)
- Test predict_failure() function for new data
- Generate SHAP explanations for sample predictions
- Export production-ready artifacts (model, scaler, metadata)
- Simulate actionable insights (yaw optimization, maintenance alerts)

Usage: python verify.py
============================================================================
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import pickle
import json
from pathlib import Path
from datetime import datetime

# Import custom modules
from model import BiLSTMPredictor
from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support, confusion_matrix

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for verification"""
    # Paths
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    MODEL_PATH = 'data/models/bilstm_model.pth'
    SCALER_PATH = 'data/processed/feature_scaler.pkl'
    
    # Export paths for production
    EXPORT_MODEL_PATH = 'data/models/final_model.pth'
    EXPORT_SCALER_PATH = 'data/models/scaler.npy'
    EXPORT_METADATA_PATH = 'data/models/model_metadata.json'
    
    # Model parameters
    INPUT_SIZE = 4
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    SEQUENCE_LENGTH = 72
    
    # Performance targets (from spec)
    TARGET_ACCURACY = 0.85
    TARGET_PRECISION = 0.80
    TARGET_AUC = 0.85
    
    # Feature names
    FEATURE_NAMES = ['wind_speed', 'vibration', 'gearbox_temperature', 'yaw_position']
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# 1. Load All Artifacts
# ============================================================================
def load_artifacts():
    """Load model, scaler, and data for verification."""
    print("="*80)
    print("PHASE 2 VERIFICATION - Loading Artifacts")
    print("="*80)
    
    # Load model
    print(f"\n[1/3] Loading trained model from {config.MODEL_PATH}...")
    model = BiLSTMPredictor(
        input_size=config.INPUT_SIZE,
        hidden_size=config.HIDDEN_SIZE,
        num_layers=config.NUM_LAYERS
    ).to(config.DEVICE)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=config.DEVICE))
    model.eval()
    print(f"   Model loaded successfully. Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Load scaler
    print(f"\n[2/3] Loading feature scaler from {config.SCALER_PATH}...")
    with open(config.SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    print(f"   Scaler loaded successfully.")
    print(f"   Feature ranges: min={scaler.data_min_}, max={scaler.data_max_}")
    
    # Load sequences
    print(f"\n[3/3] Loading test sequences from {config.SEQUENCE_PATH}...")
    X_train, y_train, X_test, y_test = torch.load(config.SEQUENCE_PATH)
    print(f"   Train: X={X_train.shape}, y={y_train.shape}")
    print(f"   Test:  X={X_test.shape}, y={y_test.shape}")
    print(f"   Test failure rate: {y_test.mean().item()*100:.2f}%")
    
    return model, scaler, (X_train, y_train, X_test, y_test)

# ============================================================================
# 2. Full Model Evaluation
# ============================================================================
def evaluate_full(model, X_test, y_test, optimal_threshold=0.75):
    """Comprehensive evaluation against targets."""
    print("\n" + "="*80)
    print("FULL MODEL EVALUATION")
    print(f"Using optimal threshold: {optimal_threshold}")
    print("="*80)
    
    model.eval()
    with torch.no_grad():
        X_test_gpu = X_test.to(config.DEVICE)
        y_test_gpu = y_test.to(config.DEVICE)
        
        # Get predictions (logits from BCEWithLogitsLoss training)
        logits = model(X_test_gpu)
        probs = torch.sigmoid(logits)  # Apply sigmoid for inference
        preds = (probs >= optimal_threshold).float()  # Use optimal threshold
        
        # Convert to numpy for metrics
        y_true = y_test_gpu.cpu().numpy()
        y_pred = preds.cpu().numpy()
        y_prob = probs.cpu().numpy()
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_prob)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    
    # Print results
    print(f"\nPerformance Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} {'✓' if accuracy >= config.TARGET_ACCURACY else '✗'} (target: {config.TARGET_ACCURACY})")
    print(f"  AUC-ROC:   {auc:.4f} {'✓' if auc >= config.TARGET_AUC else '✗'} (target: {config.TARGET_AUC})")
    print(f"  Precision: {precision:.4f} {'✓' if precision >= config.TARGET_PRECISION else '✗'} (target: {config.TARGET_PRECISION})")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]:4d}  |  FP: {cm[0,1]:4d}")
    print(f"  FN: {cm[1,0]:4d}  |  TP: {cm[1,1]:4d}")
    
    # Overall pass/fail
    all_passed = (accuracy >= config.TARGET_ACCURACY and 
                  auc >= config.TARGET_AUC and 
                  precision >= config.TARGET_PRECISION)
    
    if all_passed:
        print("\n" + "="*80)
        print("✓ ALL PERFORMANCE TARGETS MET!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ SOME TARGETS NOT MET - Review model/training")
        print("="*80)
    
    return {
        'accuracy': float(accuracy),
        'auc': float(auc),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'targets_met': all_passed
    }

# ============================================================================
# 3. Prediction Function for New Data
# ============================================================================
def predict_failure(model, scaler, new_data_df, threshold=0.75, return_explanation=False):
    """
    Predict failure for new 72-hour sequence data.
    
    Args:
        model: Trained BiLSTMPredictor
        scaler: Fitted MinMaxScaler
        new_data_df: DataFrame with columns ['wind_speed', 'vibration', 'gearbox_temperature', 'yaw_position']
                     Must have exactly 72 rows (or will use last 72)
        threshold: Decision threshold (default 0.75 optimized for precision>0.80)
        return_explanation: If True, return SHAP values
        
    Returns:
        dict with 'probability', 'prediction', 'action', 'explanation' (optional)
    """
    # Prepare data
    if len(new_data_df) < config.SEQUENCE_LENGTH:
        raise ValueError(f"Need at least {config.SEQUENCE_LENGTH} timesteps, got {len(new_data_df)}")
    
    # Take last 72 timesteps
    seq_data = new_data_df[config.FEATURE_NAMES].iloc[-config.SEQUENCE_LENGTH:].values
    
    # Scale features
    seq_scaled = scaler.transform(seq_data)
    
    # Convert to tensor
    seq_tensor = torch.tensor(seq_scaled, dtype=torch.float32).unsqueeze(0).to(config.DEVICE)  # (1, 72, 4)
    
    # Predict
    model.eval()
    with torch.no_grad():
        logit = model(seq_tensor)
        prob = torch.sigmoid(logit).item()
        pred = int(prob >= threshold)  # Use optimized threshold
    
    # Generate action
    if pred == 1:
        action = f"⚠️ ALERT: High failure risk ({prob*100:.1f}%). Schedule gearbox inspection within 72 hours."
    else:
        action = f"✓ Normal operation ({prob*100:.1f}% risk). Optimize yaw angle by +15% for potential +2% energy output."
    
    result = {
        'probability': prob,
        'prediction': pred,
        'prediction_label': 'FAILURE' if pred == 1 else 'NORMAL',
        'action': action
    }
    
    # Optional: Add SHAP explanation
    if return_explanation:
        try:
            import shap
            # For speed, use a simple gradient explanation
            seq_tensor.requires_grad = True
            output = model(seq_tensor)
            output.backward()
            
            # Gradient-based importance (simple proxy for SHAP)
            importance = seq_tensor.grad.abs().mean(dim=1).squeeze().cpu().numpy()  # (4,)
            importance_pct = (importance / importance.sum()) * 100
            
            result['explanation'] = {
                feat: f"{imp:.1f}%" 
                for feat, imp in zip(config.FEATURE_NAMES, importance_pct)
            }
        except Exception as e:
            result['explanation'] = f"Error generating explanation: {str(e)}"
    
    return result

# ============================================================================
# 4. Test Predict Function
# ============================================================================
def test_predict_function(model, scaler, X_test):
    """Test the predict_failure function on sample data."""
    print("\n" + "="*80)
    print("TESTING PREDICT_FAILURE FUNCTION")
    print("="*80)
    
    # Convert a test sequence to DataFrame format
    sample_idx = 0
    sample_seq = X_test[sample_idx].numpy()  # (72, 4)
    
    # Create DataFrame
    sample_df = pd.DataFrame(sample_seq, columns=config.FEATURE_NAMES)
    
    # Inverse transform to get original scale (for display)
    sample_original = scaler.inverse_transform(sample_seq)
    
    print(f"\nTest Sample {sample_idx + 1}:")
    print(f"  Last timestep values (original scale):")
    for i, feat in enumerate(config.FEATURE_NAMES):
        print(f"    {feat:25s}: {sample_original[-1, i]:.4f}")
    
    # Make prediction
    result = predict_failure(model, scaler, sample_df, return_explanation=True)
    
    print(f"\nPrediction Results:")
    print(f"  Probability: {result['probability']:.4f}")
    print(f"  Prediction:  {result['prediction_label']}")
    print(f"  Action:      {result['action']}")
    
    if 'explanation' in result:
        print(f"\nFeature Importance (Gradient-based):")
        for feat, imp in result['explanation'].items():
            print(f"    {feat:25s}: {imp}")
    
    return result

# ============================================================================
# 5. Export Production Artifacts
# ============================================================================
def export_production_artifacts(model, scaler, metrics):
    """Export model and scaler for Phase 3 integration."""
    print("\n" + "="*80)
    print("EXPORTING PRODUCTION ARTIFACTS")
    print("="*80)
    
    Path(config.EXPORT_MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    # Export model
    print(f"\n[1/3] Exporting model to {config.EXPORT_MODEL_PATH}...")
    torch.save(model.state_dict(), config.EXPORT_MODEL_PATH)
    print(f"   Model exported successfully.")
    
    # Export scaler as numpy array (for non-Python integrations)
    print(f"\n[2/3] Exporting scaler to {config.EXPORT_SCALER_PATH}...")
    scaler_params = {
        'data_min': scaler.data_min_,
        'data_max': scaler.data_max_,
        'data_range': scaler.data_range_
    }
    np.save(config.EXPORT_SCALER_PATH, scaler_params)
    print(f"   Scaler exported successfully.")
    
    # Export metadata
    print(f"\n[3/3] Exporting metadata to {config.EXPORT_METADATA_PATH}...")
    metadata = {
        'model_type': 'BiLSTM',
        'model_architecture': {
            'input_size': config.INPUT_SIZE,
            'hidden_size': config.HIDDEN_SIZE,
            'num_layers': config.NUM_LAYERS,
            'bidirectional': True
        },
        'sequence_length': config.SEQUENCE_LENGTH,
        'feature_names': config.FEATURE_NAMES,
        'performance_metrics': metrics,
        'targets': {
            'accuracy': config.TARGET_ACCURACY,
            'precision': config.TARGET_PRECISION,
            'auc': config.TARGET_AUC
        },
        'training_date': datetime.now().isoformat(),
        'device': str(config.DEVICE),
        'usage': 'Load model with BiLSTMPredictor, scaler with pickle/numpy, predict 72-hour sequences'
    }
    
    with open(config.EXPORT_METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   Metadata exported successfully.")
    
    print("\n" + "="*80)
    print("✓ ALL ARTIFACTS EXPORTED FOR PHASE 3")
    print("="*80)
    print(f"\nFiles created:")
    print(f"  - {config.EXPORT_MODEL_PATH}")
    print(f"  - {config.EXPORT_SCALER_PATH}")
    print(f"  - {config.EXPORT_METADATA_PATH}")

# ============================================================================
# Main Verification
# ============================================================================
def main():
    """Main verification workflow."""
    print("\n" + "="*80)
    print("WINDGUARD AI - PHASE 2 FINAL VERIFICATION")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Device: {config.DEVICE}")
    print("="*80)
    
    try:
        # Step 1: Load artifacts
        model, scaler, (X_train, y_train, X_test, y_test) = load_artifacts()
        
        # Step 2: Full evaluation
        metrics = evaluate_full(model, X_test, y_test)
        
        # Step 3: Test predict function
        prediction_result = test_predict_function(model, scaler, X_test)
        
        # Step 4: Export production artifacts
        export_production_artifacts(model, scaler, metrics)
        
        # Final summary
        print("\n" + "="*80)
        print("VERIFICATION COMPLETE!")
        print("="*80)
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy:  {metrics['accuracy']:.2%}")
        print(f"   AUC:       {metrics['auc']:.2%}")
        print(f"   Precision: {metrics['precision']:.2%}")
        print(f"\n✓ Targets Met: {'YES' if metrics['targets_met'] else 'NO'}")
        print(f"\n🚀 Next Steps:")
        print(f"   1. Review exported files in data/models/")
        print(f"   2. Integrate with Phase 3 dashboard (Streamlit)")
        print(f"   3. Test predict_failure() with live data")
        print(f"   4. Deploy model to production environment")
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ VERIFICATION FAILED")
        print("="*80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
