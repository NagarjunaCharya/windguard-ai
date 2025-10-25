"""
============================================================================
WindGuard AI - Phase 2: Model Architectures
============================================================================
Description: Defines the PyTorch model architectures for predictive
             maintenance, including a BiLSTM model and a hybrid
             BiLSTM-GNN model.

Models:
- BiLSTMPredictor: A standard BiLSTM for time-series prediction.
- HybridBiLSTMGNN: A hybrid model combining BiLSTM for temporal feature
                   extraction and a GNN for modeling inter-turbine
                   dependencies.

Usage: This script is imported by other scripts (train.py, evaluate.py, etc.)
       and is not meant to be run directly.
============================================================================
"""

import torch
import torch.nn as nn

# ============================================================================
# Configuration
# ============================================================================
# Define device for training
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ============================================================================
# 1. BiLSTM Model
# ============================================================================
class BiLSTMPredictor(nn.Module):
    """
    A Bidirectional LSTM model for wind turbine failure prediction.
    """
    def __init__(self, input_size=4, hidden_size=64, num_layers=2, dropout=0.2):
        """
        Initialize the BiLSTM model.
        
        Args:
            input_size (int): Number of input features.
            hidden_size (int): Number of features in the hidden state.
            num_layers (int): Number of recurrent layers.
            dropout (float): Dropout probability.
        """
        super(BiLSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size * 2, 1) # *2 for bidirectional
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        """
        Forward pass through the model.
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_len, features).
            
        Returns:
            torch.Tensor: Output tensor of shape (batch_size, 1).
        """
        # Initialize hidden and cell states
        h0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size).to(device)
        
        # LSTM forward pass
        out, _ = self.lstm(x, (h0, c0))
        
        # We only need the output of the last time step
        out = out[:, -1, :]
        
        # Apply dropout and fully connected layer
        out = self.dropout(out)
        out = self.fc(out)
        
        # Note: For BCEWithLogitsLoss, we don't apply sigmoid here
        # If you're using BCELoss, uncomment the next line
        # out = self.sigmoid(out)
        
        return out

# ============================================================================
# Model Testing
# ============================================================================
def test_models():
    """Function to test model instantiation and forward passes."""
    print("🧪 Testing BiLSTM model architecture...")
    
    # --- Test BiLSTMPredictor ---
    print("\n--- Testing BiLSTMPredictor ---")
    try:
        model_bilstm = BiLSTMPredictor().to(device)
        print(model_bilstm)
        
        # Mock input
        mock_input = torch.rand(32, 72, 4).to(device) # (batch, seq_len, features)
        output = model_bilstm(mock_input)
        
        print(f"Input shape: {mock_input.shape}")
        print(f"Output shape: {output.shape}")
        assert output.shape == (32, 1)
        print("✅ BiLSTM test passed!")
    except Exception as e:
        print(f"❌ BiLSTM test failed: {e}")

if __name__ == "__main__":
    test_models()
