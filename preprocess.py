"""
============================================================================
WindGuard AI - Phase 2: Data Preprocessing
============================================================================
Description: Loads processed data from Phase 1, creates time-series
             sequences, adds failure labels, and prepares data for
             training the BiLSTM model.

Features:
- Load normalized data from train_data.csv
- Generate binary 'failure' labels based on thresholds
- Create sequences for time-series forecasting (72-hour lookback)
- Augment data if sequence count is low
- Split into training and testing sets
- Save processed tensors and scaler for later use

Usage: python preprocess.py
============================================================================
"""

import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os
import pickle

# ============================================================================
# Configuration
# ============================================================================
class Config:
    """Configuration for data preprocessing"""
    # Paths
    PROCESSED_DATA_PATH = 'data/processed/train_data.csv'
    OUTPUT_DIR = 'data/processed'
    SEQUENCE_PATH = os.path.join(OUTPUT_DIR, 'sequences.pt')
    SCALER_PATH = os.path.join(OUTPUT_DIR, 'feature_scaler.pkl')

    # Sequence parameters
    SEQUENCE_LENGTH = 72
    FEATURE_COLS = ['wind_speed', 'vibration', 'gearbox_temperature', 'yaw_position']  # Correct columns from data
    
    # Labeling thresholds (CRITICAL: as per spec - vibration >0.6 OR gearbox_temp >0.85 on normalized data)
    VIBRATION_THRESHOLD = 0.6
    TEMP_THRESHOLD = 0.85
    
    # Data augmentation
    MIN_SEQUENCES_FOR_AUGMENTATION = 500
    AUGMENTATION_NOISE_STD = 0.01
    
    # Splitting
    TEST_SIZE = 0.2
    RANDOM_STATE = 42

config = Config()

# ============================================================================
# Helper Functions
# ============================================================================
def create_sequences(data: np.ndarray, labels: np.ndarray, seq_length: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Create time-series sequences from data.
    
    Args:
        data (np.ndarray): The feature data.
        labels (np.ndarray): The failure labels.
        seq_length (int): The length of each sequence.
        
    Returns:
        A tuple containing sequence data (X) and corresponding labels (y).
    """
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        # The label for a sequence is the failure status at the end of the sequence
        y.append(labels[i + seq_length - 1])
    return np.array(X), np.array(y)

# ============================================================================
# Main Preprocessing Logic
# ============================================================================
def main():
    """Main function to run the preprocessing pipeline."""
    print("🌀 Starting Phase 2: Data Preprocessing...")

    # Create output directory if it doesn't exist
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # 1. Load Data
    print(f"📂 Loading data from {config.PROCESSED_DATA_PATH}...")
    try:
        df = pd.read_csv(config.PROCESSED_DATA_PATH, parse_dates=['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
    except FileNotFoundError:
        print(f"❌ Error: Data file not found at {config.PROCESSED_DATA_PATH}")
        print("   Please run Phase 1 data ingestion first.")
        return

    print(f"   Loaded {len(df)} records.")

    # 2. Add Failure Labels
    print("🏷️  Generating failure labels...")
    df['failure'] = (
        (df['vibration'] > config.VIBRATION_THRESHOLD) |
        (df['gearbox_temperature'] > config.TEMP_THRESHOLD)
    ).astype(int)
    
    failure_rate = df['failure'].mean() * 100
    print(f"   Failure rate: {failure_rate:.2f}%")
    print(f"   Failure counts:\n{df['failure'].value_counts()}")

    # 3. Feature Scaling (or load existing scaler)
    print("⚖️  Scaling features...")
    scaler = MinMaxScaler()
    df[config.FEATURE_COLS] = scaler.fit_transform(df[config.FEATURE_COLS])
    
    # Save the scaler
    with open(config.SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"   Scaler saved to {config.SCALER_PATH}")

    # 4. Create Sequences
    print(f"🔄 Creating sequences with length {config.SEQUENCE_LENGTH}...")
    feature_data = df[config.FEATURE_COLS].values
    label_data = df['failure'].values
    
    X, y = create_sequences(feature_data, label_data, config.SEQUENCE_LENGTH)
    print(f"   Created {len(X)} sequences.")

    # 5. Data Augmentation (if needed)
    if len(X) < config.MIN_SEQUENCES_FOR_AUGMENTATION:
        print(f"   Sequence count ({len(X)}) is low. Augmenting data...")
        noise = np.random.normal(0, config.AUGMENTATION_NOISE_STD, X.shape)
        X_augmented = X + noise
        X = np.concatenate([X, X_augmented], axis=0)
        y = np.concatenate([y, y], axis=0)
        print(f"   Augmented sequence count: {len(X)}")

    # 6. Split Data
    print(f"✂️  Splitting data into train/test sets (test_size={config.TEST_SIZE})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
    )
    print(f"   Train set: {len(X_train)} sequences")
    print(f"   Test set:  {len(X_test)} sequences")

    # 7. Convert to Tensors
    print("🧠 Converting data to PyTorch tensors...")
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    print(f"   X_train shape: {X_train_tensor.shape}")
    print(f"   y_train shape: {y_train_tensor.shape}")
    print(f"   X_test shape:  {X_test_tensor.shape}")
    print(f"   y_test shape:  {y_test_tensor.shape}")

    # 8. Save Processed Data
    print(f"💾 Saving processed sequences to {config.SEQUENCE_PATH}...")
    torch.save((X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor), config.SEQUENCE_PATH)

    print("\n" + "="*80)
    print("✅ Preprocessing complete!")
    print("   Next steps: Run `train.py` to train the model.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
