# transaction_model.py

from dataclasses import dataclass


@dataclass
class TransactionModel:
    user_id: str
    amount: float
    timestamp: int
    merchant_id: str
    ip_address: str