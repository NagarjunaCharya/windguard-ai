"""
============================================================================
WindGuard AI - Phase 2: Model Training
============================================================================
Description: This script trains the BiLSTM model on the preprocessed
             time-series sequences. It handles class imbalance, logs training
             progress, plots the loss curve, and saves the trained model.

Features:
- Loads preprocessed data from `sequences.pt`
- Initializes the BiLSTMPredictor model
- Implements a training loop with Adam optimizer
- Uses BCELoss with `pos_weight` to handle class imbalance
- Evaluates on a validation set periodically
- Plots and saves the training and validation loss curves
- Saves the final trained model state dictionary

Usage: python train.py
============================================================================
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import matplotlib.pyplot as plt
import numpy as np
import os

# Import the model from model.py
from model import BiLSTMPredictor

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for model training"""
    # Paths
    SEQUENCE_PATH = 'data/processed/sequences.pt'
    MODEL_SAVE_PATH = 'data/models/bilstm_model.pth'
    LOSS_PLOT_PATH = 'results/bilstm_loss.png'
    
    # Model parameters
    INPUT_SIZE = 4
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    DROPOUT = 0.2
    
    # Training parameters
    NUM_EPOCHS = 50
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001
    VALIDATION_SPLIT = 0.2
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

config = Config()

# ============================================================================
# Main Training Logic
# ============================================================================
def main():
    """Main function to run the model training."""
    print("🌀 Starting Phase 2: Model Training...")
    print(f"   Using device: {config.DEVICE}")

    # Create results directory
    os.makedirs(os.path.dirname(config.LOSS_PLOT_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(config.MODEL_SAVE_PATH), exist_ok=True)

    # 1. Load Data
    print(f"📂 Loading preprocessed data from {config.SEQUENCE_PATH}...")
    try:
        X_train_full, y_train_full, _, _ = torch.load(config.SEQUENCE_PATH)
    except FileNotFoundError:
        print(f"❌ Error: Sequence file not found at {config.SEQUENCE_PATH}")
        print("   Please run `preprocess.py` first.")
        return

    # Create full dataset
    full_train_dataset = TensorDataset(X_train_full, y_train_full)

    # Split into training and validation sets
    val_size = int(len(full_train_dataset) * config.VALIDATION_SPLIT)
    train_size = len(full_train_dataset) - val_size
    train_dataset, val_dataset = random_split(full_train_dataset, [train_size, val_size])

    # Create DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False)
    
    print(f"   Training set size: {len(train_dataset)}")
    print(f"   Validation set size: {len(val_dataset)}")

    # 2. Handle Class Imbalance
    print("⚖️  Calculating positive weight for class imbalance...")
    # Calculate pos_weight from the full training set labels
    num_positives = y_train_full.sum()
    num_negatives = len(y_train_full) - num_positives
    pos_weight = num_negatives / num_positives if num_positives > 0 else torch.tensor(1.0)
    print(f"   Positive weight: {pos_weight:.2f}")

    # 3. Initialize Model, Loss, and Optimizer
    print("🧠 Initializing BiLSTM model...")
    model = BiLSTMPredictor(
        input_size=config.INPUT_SIZE,
        hidden_size=config.HIDDEN_SIZE,
        num_layers=config.NUM_LAYERS,
        dropout=config.DROPOUT
    ).to(config.DEVICE)
    
    print(model)
    
    criterion = nn.BCELoss(pos_weight=pos_weight.to(config.DEVICE))
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)

    # 4. Training Loop
    print("\n" + "="*80)
    print("🚀 Starting training loop...")
    print("="*80)
    
    train_losses, val_losses = [], []
    best_val_loss = float('inf')

    for epoch in range(config.NUM_EPOCHS):
        # --- Training ---
        model.train()
        total_train_loss = 0
        for i, (sequences, labels) in enumerate(train_loader):
            sequences = sequences.to(config.DEVICE)
            labels = labels.to(config.DEVICE)
            
            # Forward pass
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            
            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_train_loss += loss.item()
        
        avg_train_loss = total_train_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # --- Validation ---
        model.eval()
        total_val_loss = 0
        with torch.no_grad():
            for sequences, labels in val_loader:
                sequences = sequences.to(config.DEVICE)
                labels = labels.to(config.DEVICE)
                outputs = model(sequences)
                loss = criterion(outputs, labels)
                total_val_loss += loss.item()
        
        avg_val_loss = total_val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        # Print progress
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{config.NUM_EPOCHS}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

        # Save the best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), config.MODEL_SAVE_PATH)
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"   -> New best model saved to {config.MODEL_SAVE_PATH}")

    print("\n" + "="*80)
    print("✅ Training complete!")
    print(f"   Best validation loss: {best_val_loss:.4f}")
    print(f"   Model saved to {config.MODEL_SAVE_PATH}")
    print("="*80 + "\n")

    # 5. Plot and Save Loss Curve
    print(f"📊 Plotting and saving loss curve to {config.LOSS_PLOT_PATH}...")
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title('Training and Validation Loss Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(config.LOSS_PLOT_PATH)
    plt.close()
    print("   Plot saved.")

    print("\n" + "="*80)
    print("✅ Training script finished!")
    print("   Next steps: Run `evaluate.py` to evaluate the model performance.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
