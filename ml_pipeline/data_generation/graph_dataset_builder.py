import pandas as pd
import numpy as np
import os

class GraphDatasetBuilder:
    """
    FD-52: Build transaction graph dataset for GNN.
    Transforms tabular transactional data into Node and Edge lists suitable for Neo4j/PyTorch Geometric.
    """
    def __init__(self, data_path="data/synthetic_transactions.csv"):
        self.data_path = data_path
        
    def build(self, output_dir="data/graph"):
        print("Building graph dataset for GNN...")
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Input dataset {self.data_path} not found.")
            
        df = pd.read_csv(self.data_path)
        
        # Nodes: Users and Merchants
        users = pd.DataFrame({
            "node_id": df["user_id"].unique(),
            "node_type": "USER"
        })
        
        merchants = pd.DataFrame({
            "node_id": df["merchant_id"].unique(),
            "node_type": "MERCHANT"
        })
        
        nodes = pd.concat([users, merchants])
        
        # Edges: User -> Merchant (Transaction)
        edges = df[["user_id", "merchant_id", "amount", "timestamp", "is_fraud"]].copy()
        edges.columns = ["source", "target", "weight", "timestamp", "label"]
        edges["edge_type"] = "TRANSACTS_WITH"
        
        os.makedirs(output_dir, exist_ok=True)
        nodes.to_csv(os.path.join(output_dir, "nodes.csv"), index=False)
        edges.to_csv(os.path.join(output_dir, "edges.csv"), index=False)
        print(f"Graph dataset built with {len(nodes)} nodes and {len(edges)} edges.")

if __name__ == "__main__":
    builder = GraphDatasetBuilder()
    builder.build()
