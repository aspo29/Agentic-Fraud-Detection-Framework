import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os
import time
import mlflow
import mlflow.sklearn

class RandomForestTrainer:
    """
    FD-51: Train and evaluate Random Forest model.
    Supervised ensemble model evaluating explicit and derived rules.
    """
    def __init__(self, data_path="data/synthetic_transactions.csv", model_dir="artifacts/models"):
        self.data_path = data_path
        self.model_dir = model_dir
        
    def train_and_evaluate(self):
        print("Training Random Forest Classifier...")
        if not os.path.exists(self.data_path):
            print(f"Error: Dataset {self.data_path} not found.")
            return
            
        df = pd.read_csv(self.data_path)
        
        # Feature Engineering: basic features for tree model
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp'], unit='s').dt.hour
            
        # Select features
        feature_cols = ['amount', 'hour']
        X = df[feature_cols]
        y = df['is_fraud']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Start MLflow run
        mlflow.set_experiment("Fraud_Detection_RandomForest")
        with mlflow.start_run():
            # Train Model
            start_time = time.time()
            n_estimators = 100
            max_depth = 10
            clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, class_weight='balanced', random_state=42)
            clf.fit(X_train, y_train)
            
            # Evaluate
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1]
            auc_score = roc_auc_score(y_test, y_prob)
            
            print("Evaluation Report:")
            print(classification_report(y_test, y_pred))
            print(f"ROC AUC: {auc_score:.4f}")
            
            # Log to MLflow
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_metric("roc_auc", auc_score)
            mlflow.sklearn.log_model(clf, "random_forest_model")
            
            # Save model locally
            os.makedirs(self.model_dir, exist_ok=True)
            model_path = os.path.join(self.model_dir, "random_forest.pkl")
            joblib.dump(clf, model_path)
            print(f"Model saved to {model_path} in {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    trainer = RandomForestTrainer()
    trainer.train_and_evaluate()
