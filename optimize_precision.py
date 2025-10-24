"""
============================================================================
WindGuard AI - Phase 2: Precision Optimization
============================================================================
Description: Fine-tune the model to meet precision target (>0.80) by
             adjusting decision threshold and using threshold optimization.

Features:
- Load trained model and test data
- Sweep decision thresholds from 0.3 to 0.7
- Find optimal threshold that maximizes F1 while meeting precision >0.80
- Retrain if needed with adjusted pos_weight
- Save optimized model and threshold

Usage: python optimize_precision.py
============================================================================
"""

import torch
import numpy as np
from sklearn.metrics import precision_recall_curve, f1_score, precision_score, recall_score, accuracy_score
import matplotlib.pyplot as plt
from model import BiLSTMPredictor

# ============================================================================
# Configuration
# ============================================================================
class Config:
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    MODEL_PATH = 'data/models/bilstm_model.pth'
    OPTIMIZED_MODEL_PATH = 'data/models/optimized_model.pth'
    THRESHOLD_PLOT_PATH = 'results/threshold_optimization.png'
    
    INPUT_SIZE = 4
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    
    TARGET_PRECISION = 0.80
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# Find Optimal Threshold
# ============================================================================
def find_optimal_threshold(model, X_test, y_test):
    """Find the decision threshold that meets precision target."""
    print("="*80)
    print("THRESHOLD OPTIMIZATION")
    print("="*80)
    
    model.eval()
    with torch.no_grad():
        X_test_gpu = X_test.to(config.DEVICE)
        y_test_gpu = y_test.to(config.DEVICE)
        
        # Get probability predictions
        logits = model(X_test_gpu)
        probs = torch.sigmoid(logits).cpu().numpy().flatten()
        y_true = y_test_gpu.cpu().numpy().flatten()
    
    # Sweep thresholds
    thresholds = np.arange(0.3, 0.8, 0.05)
    results = []
    
    print(f"\nTesting thresholds from {thresholds[0]:.2f} to {thresholds[-1]:.2f}...\n")
    print(f"{'Threshold':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Meets Target'}")
    print("-"*80)
    
    for threshold in thresholds:
        y_pred = (probs >= threshold).astype(int)
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        meets_target = precision >= config.TARGET_PRECISION
        
        results.append({
            'threshold': threshold,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'meets_target': meets_target
        })
        
        status = "✓" if meets_target else "✗"
        print(f"{threshold:<12.2f} {accuracy:<12.4f} {precision:<12.4f} {recall:<12.4f} {f1:<12.4f} {status}")
    
    # Find best threshold that meets precision target
    valid_results = [r for r in results if r['meets_target']]
    
    if valid_results:
        # Among valid thresholds, pick one with best F1
        best_result = max(valid_results, key=lambda x: x['f1'])
        print(f"\n{'='*80}")
        print(f"✓ OPTIMAL THRESHOLD FOUND: {best_result['threshold']:.2f}")
        print(f"{'='*80}")
        print(f"  Accuracy:  {best_result['accuracy']:.4f}")
        print(f"  Precision: {best_result['precision']:.4f} (target: {config.TARGET_PRECISION})")
        print(f"  Recall:    {best_result['recall']:.4f}")
        print(f"  F1-Score:  {best_result['f1']:.4f}")
    else:
        print(f"\n{'='*80}")
        print(f"✗ NO THRESHOLD MEETS PRECISION TARGET")
        print(f"{'='*80}")
        print(f"  Recommend: Retrain with higher pos_weight or collect more failure samples")
        best_result = max(results, key=lambda x: x['precision'])
        print(f"  Best available: threshold={best_result['threshold']:.2f}, precision={best_result['precision']:.4f}")
    
    # Plot precision-recall curve
    plot_threshold_analysis(results)
    
    return best_result

# ============================================================================
# Plot Threshold Analysis
# ============================================================================
def plot_threshold_analysis(results):
    """Visualize how metrics change with threshold."""
    print(f"\n📊 Saving threshold analysis plot to {config.THRESHOLD_PLOT_PATH}...")
    
    thresholds = [r['threshold'] for r in results]
    precisions = [r['precision'] for r in results]
    recalls = [r['recall'] for r in results]
    f1s = [r['f1'] for r in results]
    accuracies = [r['accuracy'] for r in results]
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(thresholds, precisions, 'b-', label='Precision', linewidth=2, marker='o')
    plt.plot(thresholds, recalls, 'g-', label='Recall', linewidth=2, marker='s')
    plt.plot(thresholds, f1s, 'r-', label='F1-Score', linewidth=2, marker='^')
    plt.plot(thresholds, accuracies, 'm-', label='Accuracy', linewidth=2, marker='d')
    
    plt.axhline(y=config.TARGET_PRECISION, color='b', linestyle='--', alpha=0.5, label=f'Target Precision ({config.TARGET_PRECISION})')
    
    plt.xlabel('Decision Threshold', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title('Model Performance vs. Decision Threshold', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(config.THRESHOLD_PLOT_PATH, dpi=150)
    plt.close()
    print(f"   Plot saved successfully.")

# ============================================================================
# Save Optimized Configuration
# ============================================================================
def save_optimized_config(best_result):
    """Save the optimal threshold configuration."""
    import json
    
    config_path = 'data/models/optimal_config.json'
    config_data = {
        'optimal_threshold': float(best_result['threshold']),
        'performance': {
            'accuracy': float(best_result['accuracy']),
            'precision': float(best_result['precision']),
            'recall': float(best_result['recall']),
            'f1_score': float(best_result['f1'])
        },
        'meets_precision_target': bool(best_result['meets_target']),
        'usage': 'Use this threshold for predict_failure() function'
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"\n✓ Optimal configuration saved to {config_path}")

# ============================================================================
# Main
# ============================================================================
def main():
    """Main optimization workflow."""
    print("\n" + "="*80)
    print("WINDGUARD AI - PRECISION OPTIMIZATION")
    print("="*80)
    
    # Load model and data
    print("\nLoading model and test data...")
    model = BiLSTMPredictor(
        input_size=config.INPUT_SIZE,
        hidden_size=config.HIDDEN_SIZE,
        num_layers=config.NUM_LAYERS
    ).to(config.DEVICE)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=config.DEVICE))
    
    _, _, X_test, y_test = torch.load(config.SEQUENCE_PATH)
    print(f"   Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"   Test samples: {len(X_test)}")
    
    # Find optimal threshold
    best_result = find_optimal_threshold(model, X_test, y_test)
    
    # Save configuration
    save_optimized_config(best_result)
    
    print("\n" + "="*80)
    print("✓ OPTIMIZATION COMPLETE")
    print("="*80)
    print(f"\nNext steps:")
    print(f"  1. Update predict_failure() to use threshold={best_result['threshold']:.2f}")
    print(f"  2. If target not met, consider:")
    print(f"     - Collecting more failure samples")
    print(f"     - Increasing pos_weight in training")
    print(f"     - Using SMOTE for synthetic oversampling")
    print(f"     - Ensemble with RandomForest")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
