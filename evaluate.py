"""
============================================================================
WindGuard AI - Phase 2: Model Evaluation
============================================================================
Description: This script evaluates the trained BiLSTM model on the test set.
             It calculates and reports key performance metrics such as
             accuracy, AUC-ROC, precision, recall, and F1-score.

Features:
- Loads the trained model from `bilstm_model.pth`
- Loads the test data from `sequences.pt`
- Defines a function to compute performance metrics
- Prints a classification report and confusion matrix
- Simulates a simple action based on prediction outcomes

Usage: python evaluate.py
============================================================================
"""

import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_fscore_support, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# Import the model from model.py
from model import BiLSTMPredictor

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for model evaluation"""
    # Paths
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    MODEL_PATH = 'data/models/bilstm_model.pth'
    RESULTS_DIR = 'results'
    CONFUSION_MATRIX_PATH = os.path.join(RESULTS_DIR, 'confusion_matrix.png')
    
    # Model parameters (must match training)
    INPUT_SIZE = 4
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    
    # Evaluation parameters
    BATCH_SIZE = 32
    PREDICTION_THRESHOLD = 0.5
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# Evaluation Function
# ============================================================================
def evaluate_model(model, test_loader, device):
    """
    Evaluates the model on the test set.
    
    Args:
        model (nn.Module): The trained model.
        test_loader (DataLoader): DataLoader for the test set.
        device (torch.device): The device to run evaluation on.
        
    Returns:
        A tuple of (predictions, true_labels, probabilities).
    """
    print("🧪 Evaluating model on the test set...")
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences = sequences.to(device)
            labels = labels.to(device)
            
            # Get model outputs (probabilities)
            outputs = model(sequences)
            
            # Get predictions (0 or 1)
            preds = (outputs >= config.PREDICTION_THRESHOLD).float()
            
            all_probs.extend(outputs.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    return np.array(all_preds), np.array(all_labels), np.array(all_probs)

# ============================================================================
# Main Evaluation Logic
# ============================================================================
def main():
    """Main function to run the model evaluation."""
    print("🌀 Starting Phase 2: Model Evaluation...")
    print(f"   Using device: {config.DEVICE}")

    # Create results directory
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # 1. Load Test Data
    print(f"📂 Loading test data from {config.SEQUENCE_PATH}...")
    try:
        _, _, X_test, y_test = torch.load(config.SEQUENCE_PATH)
        test_dataset = TensorDataset(X_test, y_test)
        test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False)
    except FileNotFoundError:
        print(f"❌ Error: Sequence file not found at {config.SEQUENCE_PATH}")
        print("   Please run `preprocess.py` first.")
        return
    
    print(f"   Test set size: {len(test_dataset)}")

    # 2. Load Trained Model
    print(f"🧠 Loading trained model from {config.MODEL_PATH}...")
    try:
        model = BiLSTMPredictor(
            input_size=config.INPUT_SIZE,
            hidden_size=config.HIDDEN_SIZE,
            num_layers=config.NUM_LAYERS
        ).to(config.DEVICE)
        model.load_state_dict(torch.load(config.MODEL_PATH, map_location=config.DEVICE))
    except FileNotFoundError:
        print(f"❌ Error: Model file not found at {config.MODEL_PATH}")
        print("   Please run `train.py` first.")
        return

    # 3. Evaluate Model
    predictions, true_labels, probabilities = evaluate_model(model, test_loader, config.DEVICE)

    # 4. Calculate and Print Metrics
    accuracy = accuracy_score(true_labels, predictions)
    auc = roc_auc_score(true_labels, probabilities)
    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary')

    print("\n" + "="*80)
    print("📊 Evaluation Results")
    print("="*80)
    print(f"   -> Accuracy:  {accuracy:.4f}")
    print(f"   -> AUC-ROC:   {auc:.4f}")
    print(f"   -> Precision: {precision:.4f}")
    print(f"   -> Recall:    {recall:.4f}")
    print(f"   -> F1-Score:  {f1:.4f}")
    print("="*80 + "\n")

    # 5. Plot and Save Confusion Matrix
    print(f"🎨 Plotting confusion matrix to {config.CONFUSION_MATRIX_PATH}...")
    cm = confusion_matrix(true_labels, predictions)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['No Failure', 'Failure'],
                yticklabels=['No Failure', 'Failure'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.savefig(config.CONFUSION_MATRIX_PATH)
    plt.close()
    print("   Confusion matrix saved.")

    # 6. Simulate Actionable Insights
    print("\n" + "="*80)
    print("🤖 Simulating Actionable Insights (Sample of 5 predictions)")
    print("="*80)
    for i in range(min(5, len(predictions))):
        prob = probabilities[i][0]
        pred = predictions[i][0]
        
        if pred == 0:
            print(f"Prediction {i+1}: Probability={prob:.2f} -> No failure predicted.")
            print("   ACTION: Optimize yaw by 15% for potential +2% energy output.")
        else:
            print(f"Prediction {i+1}: Probability={prob:.2f} -> FAILURE PREDICTED.")
            print("   ACTION: Schedule gearbox inspection within 72 hours.")
    print("="*80 + "\n")

    print("\n" + "="*80)
    print("✅ Evaluation script finished!")
    print("   Next steps: Run `tune.py` for hyperparameter optimization or `explain.py` for model explainability.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
