import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import time

class IsolationForestTrainer:
    """
    FD-49: Train and evaluate Isolation Forest model.
    Unsupervised anomaly detection to identify outliers in amount and frequency.
    """
    def __init__(self, data_path="data/synthetic_transactions.csv", model_dir="artifacts/models"):
        self.data_path = data_path
        self.model_dir = model_dir
        
    def train_and_evaluate(self):
        print("Training Isolation Forest Model...")
        if not os.path.exists(self.data_path):
            print(f"Error: Dataset {self.data_path} not found.")
            return
            
        df = pd.read_csv(self.data_path)
        
        # Simple feature engineering
        # We assume dataset has 'amount', 'timestamp'
        # In reality, we'd compute frequency features here
        features = df[['amount']].copy()
        
        # Train Isolation Forest
        start_time = time.time()
        clf = IsolationForest(n_estimators=100, contamination=0.03, random_state=42)
        clf.fit(features)
        
        # Predict
        predictions = clf.predict(features)
        
        # Evaluate against the synthetic ground truth if available
        if 'is_fraud' in df.columns:
            df['pred_anomaly'] = [1 if p == -1 else 0 for p in predictions]
            fraud_detected = df[(df['is_fraud'] == 1) & (df['pred_anomaly'] == 1)].shape[0]
            total_fraud = df[df['is_fraud'] == 1].shape[0]
            print(f"Evaluation: Detected {fraud_detected}/{total_fraud} anomalies.")
        
        # Save model
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, "isolation_forest.pkl")
        joblib.dump(clf, model_path)
        print(f"Model saved to {model_path} in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    trainer = IsolationForestTrainer()
    trainer.train_and_evaluate()
