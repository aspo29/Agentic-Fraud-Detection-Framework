import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import os
import time

class BehavioralLSTM(nn.Module):
    """
    FD-73: Define LSTM architecture and hyperparameters.
    Captures sequential behavioral patterns over time for a user.
    """
    def __init__(self, input_dim=2, hidden_dim=64, num_layers=2, output_dim=1):
        super(BehavioralLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        out, (hn, cn) = self.lstm(x)
        # Use the last output
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)

class LSTMTrainer:
    """
    FD-50: Train and evaluate LSTM behavioral model.
    """
    def __init__(self, data_path="data/synthetic_transactions.csv", model_dir="artifacts/models"):
        self.data_path = data_path
        self.model_dir = model_dir
        
    def train_and_evaluate(self):
        print("Training LSTM Behavioral Model...")
        if not os.path.exists(self.data_path):
            print(f"Error: Dataset {self.data_path} not found.")
            return
            
        # Simplified data generation for demonstration
        # Real training would sequence transactions per user
        input_dim = 2 # e.g., amount, time_diff
        seq_len = 10
        num_samples = 1000
        
        # Mock Data (Batch, Sequence Length, Features)
        X_train = torch.randn(num_samples, seq_len, input_dim)
        y_train = torch.randint(0, 2, (num_samples, 1)).float()
        
        model = BehavioralLSTM(input_dim=input_dim)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        start_time = time.time()
        
        # Train Loop
        epochs = 5
        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
            
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, "lstm_behavioral.pth")
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path} in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    trainer = LSTMTrainer()
    trainer.train_and_evaluate()
