import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import os

class SyntheticDataGenerator:
    """
    FD-48: Generate synthetic training dataset for fraud detection.
    Generates realistic transactional data including normal patterns and injected anomalies.
    """
    def __init__(self, num_users=1000, num_transactions=50000, fraud_ratio=0.03):
        self.num_users = num_users
        self.num_transactions = num_transactions
        self.fraud_ratio = fraud_ratio
        
    def generate(self, output_dir="data"):
        print("Generating synthetic transactional dataset...")
        np.random.seed(42)
        random.seed(42)
        
        users = [f"U{str(i).zfill(5)}" for i in range(self.num_users)]
        merchants = [f"M{str(i).zfill(4)}" for i in range(100)]
        
        # User base profiles (for LSTM tracking)
        user_profiles = {
            u: {
                "avg_amount": np.random.lognormal(mean=4.0, sigma=1.0),
                "preferred_merchants": random.sample(merchants, 3)
            } for u in users
        }
        
        data = []
        current_time = datetime(2025, 1, 1)
        
        for i in range(self.num_transactions):
            user = random.choice(users)
            profile = user_profiles[user]
            
            is_fraud = random.random() < self.fraud_ratio
            
            if is_fraud:
                # Anomalous behavior
                amount = profile["avg_amount"] * np.random.uniform(5, 20)
                merchant = random.choice(merchants)
            else:
                # Normal behavior
                amount = np.random.normal(profile["avg_amount"], profile["avg_amount"] * 0.2)
                amount = max(1.0, amount)
                
                # 80% chance to use preferred merchant
                if random.random() < 0.8:
                    merchant = random.choice(profile["preferred_merchants"])
                else:
                    merchant = random.choice(merchants)
                    
            # Increment time slightly
            current_time += timedelta(minutes=random.randint(1, 60))
            
            data.append({
                "transaction_id": f"T{str(i).zfill(8)}",
                "user_id": user,
                "merchant_id": merchant,
                "amount": round(amount, 2),
                "timestamp": current_time.timestamp(),
                "is_fraud": int(is_fraud)
            })
            
        df = pd.DataFrame(data)
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "synthetic_transactions.csv")
        df.to_csv(filepath, index=False)
        print(f"Dataset generated with {len(df)} records at {filepath}")
        return df

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    generator.generate()
