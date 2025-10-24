"""
============================================================================
WindGuard AI - Phase 2: Model Explainability with SHAP
============================================================================
Description: This script uses the SHAP (SHapley Additive exPlanations)
             library to explain the predictions of the trained BiLSTM model.
             It generates and saves plots for both global and local
             feature importance.

Features:
- Loads the trained model and test data
- Uses SHAP's DeepExplainer for PyTorch models
- Generates a summary plot for global feature importance
- Generates a waterfall plot for a single prediction's explanation
- Adapts SHAP for time-series data by averaging SHAP values over the
  sequence length

Usage: python explain.py
============================================================================
"""

import torch
from torch.utils.data import TensorDataset
import shap
import numpy as np
import matplotlib.pyplot as plt
import os

# Import the model from model.py
from model import BiLSTMPredictor

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for model explainability"""
    # Paths
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    MODEL_PATH = 'data/models/bilstm_model.pth'
    RESULTS_DIR = 'results'
    SHAP_SUMMARY_PATH = os.path.join(RESULTS_DIR, 'shap_summary.png')
    SHAP_WATERFALL_PATH = os.path.join(RESULTS_DIR, 'shap_waterfall.png')
    
    # Model parameters (must match training)
    INPUT_SIZE = 4
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    
    # SHAP parameters
    BACKGROUND_SAMPLES = 100
    TEST_SAMPLES = 50
    
    # Feature names
    FEATURE_NAMES = ['wind_speed', 'vibration', 'gearbox_temperature', 'yaw_position']
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# Main Explainability Logic
# ============================================================================
def main():
    """Main function to run the SHAP explainability analysis."""
    print("🌀 Starting Phase 2: Model Explainability with SHAP...")
    print(f"   Using device: {config.DEVICE}")

    # Create results directory
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # 1. Load Data
    print(f"📂 Loading data from {config.SEQUENCE_PATH}...")
    try:
        X_train, _, X_test, _ = torch.load(config.SEQUENCE_PATH)
    except FileNotFoundError:
        print(f"❌ Error: Sequence file not found at {config.SEQUENCE_PATH}")
        print("   Please run `preprocess.py` first.")
        return

    # 2. Load Model
    print(f"🧠 Loading trained model from {config.MODEL_PATH}...")
    try:
        model = BiLSTMPredictor(
            input_size=config.INPUT_SIZE,
            hidden_size=config.HIDDEN_SIZE,
            num_layers=config.NUM_LAYERS
        ).to(config.DEVICE)
        model.load_state_dict(torch.load(config.MODEL_PATH, map_location=config.DEVICE))
        model.eval()
    except FileNotFoundError:
        print(f"❌ Error: Model file not found at {config.MODEL_PATH}")
        print("   Please run `train.py` first.")
        return

    # 3. Initialize SHAP Explainer
    print("✨ Initializing SHAP DeepExplainer...")
    # SHAP needs a background dataset to compute expected values
    background_data = X_train[:config.BACKGROUND_SAMPLES].to(config.DEVICE)
    
    # For LSTM, GradientExplainer is often more stable than DeepExplainer
    try:
        explainer = shap.GradientExplainer(model, background_data)
        print("   Using GradientExplainer.")
    except Exception as e:
        print(f"   GradientExplainer failed: {e}. Trying DeepExplainer.")
        try:
            explainer = shap.DeepExplainer(model, background_data)
            print("   Using DeepExplainer.")
        except Exception as e2:
            print(f"❌ SHAP explainer initialization failed: {e2}")
            print("   This can be due to model complexity or SHAP/PyTorch version incompatibilities.")
            return

    # 4. Compute SHAP Values
    print(f"🧮 Computing SHAP values for {config.TEST_SAMPLES} test samples...")
    test_samples = X_test[:config.TEST_SAMPLES].to(config.DEVICE)
    
    try:
        shap_values = explainer.shap_values(test_samples)
    except Exception as e:
        print(f"❌ SHAP value computation failed: {e}")
        return

    # The output of SHAP for time-series is (samples, seq_len, features)
    # We can average over the time dimension for a summary
    shap_values_avg_time = np.mean(shap_values, axis=1)
    test_samples_avg_time = test_samples.cpu().numpy().mean(axis=1)

    print(f"   SHAP values shape: {shap_values.shape}")
    print(f"   Averaged SHAP values shape: {shap_values_avg_time.shape}")

    # 5. Generate and Save Global Importance Plot
    print(f"📊 Generating and saving SHAP summary plot to {config.SHAP_SUMMARY_PATH}...")
    plt.figure()
    shap.summary_plot(
        shap_values_avg_time,
        features=test_samples_avg_time,
        feature_names=config.FEATURE_NAMES,
        show=False,
        plot_type="bar"
    )
    plt.title("Global Feature Importance (SHAP)")
    plt.tight_layout()
    plt.savefig(config.SHAP_SUMMARY_PATH)
    plt.close()
    print("   Summary plot saved.")

    # 6. Generate and Save Local Explanation (Waterfall Plot)
    print(f"💧 Generating and saving SHAP waterfall plot for one prediction to {config.SHAP_WATERFALL_PATH}...")
    
    # For GradientExplainer, we need to compute the base value differently
    # Use the mean prediction on the background data as the base value
    with torch.no_grad():
        background_preds = model(background_data).cpu().numpy()
        base_value = float(background_preds.mean())
    
    # Create a SHAP explanation object for the first prediction
    explanation = shap.Explanation(
        values=shap_values_avg_time[0, :, 0],  # First sample, all features, first output
        base_values=base_value,
        data=test_samples_avg_time[0],
        feature_names=config.FEATURE_NAMES
    )
    
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(explanation, show=False)
    plt.title("Local Explanation for a Single Prediction (SHAP)")
    plt.tight_layout()
    plt.savefig(config.SHAP_WATERFALL_PATH)
    plt.close()
    print("   Waterfall plot saved.")

    # 7. Interpret Results
    # Get the most important feature globally
    # SHAP values are shape (samples, features, 1), so we need to squeeze the last dimension
    mean_abs_shap = np.mean(np.abs(shap_values_avg_time.squeeze()), axis=0)
    most_important_feature_idx = np.argmax(mean_abs_shap)
    most_important_feature = config.FEATURE_NAMES[most_important_feature_idx]
    importance_percentage = float((mean_abs_shap[most_important_feature_idx] / np.sum(mean_abs_shap)) * 100)

    print("\n" + "="*80)
    print("💡 Interpretation")
    print("="*80)
    print(f"   Globally, the most important feature is '{most_important_feature}', contributing ~{importance_percentage:.1f}% to the predictions.")
    print("   Check `results/shap_summary.png` for a full breakdown.")
    print("   `results/shap_waterfall.png` shows how each feature contributed to a single prediction.")
    print("="*80 + "\n")

    print("\n" + "="*80)
    print("✅ Explainability script finished!")
    print("   This concludes the core ML modeling of Phase 2.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
