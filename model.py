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
import torch_geometric.nn as pyg_nn
from torch_geometric.data import Data

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
        
        # Apply sigmoid activation for binary classification
        out = self.sigmoid(out)
        
        return out

# ============================================================================
# 2. Hybrid BiLSTM-GNN Model (for inter-turbine analysis)
# ============================================================================
class HybridBiLSTMGNN(nn.Module):
    """
    A hybrid model combining BiLSTM for temporal analysis and GNN for
    spatial analysis across multiple turbines.
    
    NOTE: This is an advanced model. For the MVP, we focus on the BiLSTM.
          This implementation serves as a template for future expansion.
    """
    def __init__(self, input_size=4, bilstm_hidden_size=64, bilstm_layers=2,
                 gnn_hidden_size=32, dropout=0.2):
        """
        Initialize the hybrid model.
        """
        super(HybridBiLSTMGNN, self).__init__()
        
        # BiLSTM part for individual turbine sequences
        self.bilstm = BiLSTMPredictor(
            input_size=input_size,
            hidden_size=bilstm_hidden_size,
            num_layers=bilstm_layers,
            dropout=dropout
        )
        # We need to get the feature vector before the final FC layer
        self.bilstm.fc = nn.Identity()
        self.bilstm.sigmoid = nn.Identity()
        
        # GNN part for graph of turbines
        self.gnn1 = pyg_nn.GCNConv(bilstm_hidden_size * 2, gnn_hidden_size)
        self.gnn2 = pyg_nn.GCNConv(gnn_hidden_size, gnn_hidden_size)
        
        # Final classifier
        self.fc = nn.Linear(gnn_hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x_batch, edge_index):
        """
        Forward pass for the hybrid model.
        
        Args:
            x_batch (torch.Tensor): Input tensor of shape (batch_size, num_turbines, seq_len, features).
            edge_index (torch.Tensor): Graph connectivity in COO format.
            
        Returns:
            torch.Tensor: Output tensor of shape (batch_size * num_turbines, 1).
        """
        batch_size, num_turbines, seq_len, num_features = x_batch.shape
        
        # 1. Process each turbine's sequence through the BiLSTM
        # Reshape to (batch_size * num_turbines, seq_len, features)
        x_lstm_in = x_batch.view(batch_size * num_turbines, seq_len, num_features)
        
        # Get temporal features from BiLSTM
        temporal_features = self.bilstm(x_lstm_in) # Shape: (batch*num_turbines, bilstm_hidden*2)
        
        # 2. Process through GNN
        # The GNN expects node features for the entire graph. We need to handle batches.
        # For simplicity in this MVP, we process each graph in the batch independently.
        
        all_graph_outputs = []
        for i in range(batch_size):
            # Get features for the current graph in the batch
            start_idx = i * num_turbines
            end_idx = (i + 1) * num_turbines
            graph_features = temporal_features[start_idx:end_idx] # Shape: (num_turbines, features)
            
            # GNN layers
            x = self.gnn1(graph_features, edge_index)
            x = self.relu(x)
            x = self.dropout(x)
            
            x = self.gnn2(x, edge_index)
            x = self.relu(x)
            
            all_graph_outputs.append(x)
            
        # Concatenate results from all graphs in the batch
        gnn_out = torch.cat(all_graph_outputs, dim=0) # Shape: (batch*num_turbines, gnn_hidden)
        
        # 3. Final prediction
        out = self.fc(gnn_out)
        out = self.sigmoid(out)
        
        return out

# ============================================================================
# Model Testing
# ============================================================================
def test_models():
    """Function to test model instantiation and forward passes."""
    print("🧪 Testing model architectures...")
    
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

    # --- Test HybridBiLSTMGNN ---
    # NOTE: This is a simplified test for the MVP.
    print("\n--- Testing HybridBiLSTMGNN (MVP Fallback) ---")
    print("   INFO: GNN part is complex. Focusing on BiLSTM for core functionality.")
    try:
        model_hybrid = HybridBiLSTMGNN().to(device)
        print(model_hybrid)
        
        # Mock graph structure (5 turbines in a line)
        edge_index = torch.tensor([
            [0, 1, 1, 2, 2, 3, 3, 4], # Source nodes
            [1, 0, 2, 1, 3, 2, 4, 3]  # Target nodes
        ], dtype=torch.long).to(device)
        
        # Mock input for a batch of 4 graphs, each with 5 turbines
        mock_input_hybrid = torch.rand(4, 5, 72, 4).to(device) # (batch, turbines, seq, feats)
        
        output_hybrid = model_hybrid(mock_input_hybrid, edge_index)
        
        print(f"Input shape: {mock_input_hybrid.shape}")
        print(f"Edge index shape: {edge_index.shape}")
        print(f"Output shape: {output_hybrid.shape}")
        assert output_hybrid.shape == (20, 1) # 4 batches * 5 turbines
        print("✅ Hybrid BiLSTM-GNN test passed!")
        
    except Exception as e:
        print(f"❌ Hybrid BiLSTM-GNN test failed: {e}")
        print("   This is expected if PyTorch Geometric is not fully configured.")
        print("   Falling back to BiLSTM-only model is the recommended path for now.")

if __name__ == "__main__":
    test_models()
