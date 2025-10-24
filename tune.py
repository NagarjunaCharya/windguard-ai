"""
============================================================================
WindGuard AI - Phase 2: Hyperparameter Tuning with Optuna
============================================================================
Description: This script uses Optuna to perform hyperparameter tuning for
             the BiLSTM model. It searches for the best combination of
             hyperparameters to maximize validation accuracy.

Features:
- Defines an objective function for Optuna to optimize
- Searches over learning rate, hidden size, number of layers, and dropout
- Uses a subset of data and fewer epochs for faster trials
- Implements pruning for early stopping of unpromising trials
- Prints the best hyperparameters found
- Visualizes and saves parameter importances and optimization history

Usage: python tune.py
============================================================================
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import optuna
from optuna.visualization import plot_optimization_history, plot_param_importances
import os
import plotly

# Import the model from model.py
from model import BiLSTMPredictor

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for hyperparameter tuning"""
    # Paths
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    RESULTS_DIR = 'results'
    
    # Optuna settings
    N_TRIALS = 10
    TIMEOUT = 300  # seconds (5 minutes)
    
    # Training settings for each trial
    TRIAL_EPOCHS = 10
    BATCH_SIZE = 32
    VALIDATION_SPLIT = 0.2
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# Objective Function for Optuna
# ============================================================================
def objective(trial: optuna.Trial) -> float:
    """
    Defines the objective function that Optuna will minimize.
    
    Args:
        trial (optuna.Trial): A single trial in the optimization study.
        
    Returns:
        float: The validation accuracy for the trial.
    """
    # 1. Suggest Hyperparameters
    params = {
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True),
        'hidden_size': trial.suggest_categorical('hidden_size', [32, 64, 128]),
        'num_layers': trial.suggest_int('num_layers', 1, 3),
        'dropout': trial.suggest_float('dropout', 0.1, 0.5),
    }
    
    # 2. Load Data
    try:
        X_train_full, y_train_full, _, _ = torch.load(config.SEQUENCE_PATH)
    except FileNotFoundError:
        print("❌ Sequence file not found. Run preprocess.py first.")
        # Return a high value to indicate failure
        return 1.0

    full_train_dataset = TensorDataset(X_train_full, y_train_full)
    val_size = int(len(full_train_dataset) * config.VALIDATION_SPLIT)
    train_size = len(full_train_dataset) - val_size
    train_dataset, val_dataset = random_split(full_train_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False)

    # 3. Initialize Model and Optimizer
    model = BiLSTMPredictor(
        input_size=4,
        hidden_size=params['hidden_size'],
        num_layers=params['num_layers'],
        dropout=params['dropout']
    ).to(config.DEVICE)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=params['learning_rate'])
    
    # Calculate pos_weight for loss function
    num_positives = y_train_full.sum()
    num_negatives = len(y_train_full) - num_positives
    pos_weight = num_negatives / num_positives if num_positives > 0 else torch.tensor(1.0)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(config.DEVICE))

    # 4. Training and Validation Loop for the Trial
    for epoch in range(config.TRIAL_EPOCHS):
        model.train()
        for sequences, labels in train_loader:
            sequences, labels = sequences.to(config.DEVICE), labels.to(config.DEVICE)
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    # 5. Evaluate on Validation Set
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for sequences, labels in val_loader:
            sequences, labels = sequences.to(config.DEVICE), labels.to(config.DEVICE)
            outputs = model(sequences)
            predicted = (outputs >= 0.5).float()
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    val_accuracy = correct / total
    
    # Report intermediate results for pruning
    trial.report(val_accuracy, epoch)
    if trial.should_prune():
        raise optuna.exceptions.TrialPruned()
        
    return val_accuracy

# ============================================================================
# Main Tuning Logic
# ============================================================================
def main():
    """Main function to run the hyperparameter tuning."""
    print("🌀 Starting Phase 2: Hyperparameter Tuning with Optuna...")
    print(f"   Using device: {config.DEVICE}")
    print(f"   Number of trials: {config.N_TRIALS}")

    # Create results directory
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # 1. Create and Run Optuna Study
    # We want to maximize accuracy, so we set direction to 'maximize'
    study = optuna.create_study(
        direction='maximize',
        pruner=optuna.pruners.MedianPruner()
    )
    
    try:
        study.optimize(objective, n_trials=config.N_TRIALS, timeout=config.TIMEOUT)
    except Exception as e:
        print(f"❌ An error occurred during optimization: {e}")
        print("   This might be due to issues with data loading or model configuration.")
        return

    # 2. Print Results
    print("\n" + "="*80)
    print("🏆 Tuning Complete!")
    print("="*80)
    print(f"Number of finished trials: {len(study.trials)}")
    
    best_trial = study.best_trial
    print(f"Best trial value (validation accuracy): {best_trial.value:.4f}")
    
    print("\n📋 Best Hyperparameters:")
    for key, value in best_trial.params.items():
        print(f"   - {key}: {value}")
    print("="*80 + "\n")

    # 3. Save Visualizations
    print("📊 Saving visualizations...")
    
    # Plot optimization history
    history_fig = plot_optimization_history(study)
    history_fig.write_html(os.path.join(config.RESULTS_DIR, 'optuna_history.html'))
    
    # Plot parameter importances
    try:
        importance_fig = plot_param_importances(study)
        importance_fig.write_html(os.path.join(config.RESULTS_DIR, 'optuna_importance.html'))
        print(f"   Saved plots to `{config.RESULTS_DIR}/`")
    except Exception as e:
        print(f"   Could not generate parameter importance plot: {e}")
        print("   This can happen if all trials have the same parameters or if there are too few trials.")

    print("\n" + "="*80)
    print("✅ Tuning script finished!")
    print("   Next steps: Use the best hyperparameters to retrain the final model in `train.py`.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
