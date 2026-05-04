class ColdStartDetector:
    """
    FD-54: Implement cold-start detection and fallback logic.
    Identifies if a user lacks sufficient behavioral history and assigns them
    to a predefined cohort baseline (e.g., 'urban student', 'rural merchant').
    """
    def __init__(self, min_history_threshold=10):
        self.min_history_threshold = min_history_threshold
        
        # Predefined cohort baselines (mocked)
        self.cohort_baselines = {
            "urban_retail": {"avg_amount": 150.0, "freq_per_day": 3},
            "rural_merchant": {"avg_amount": 5000.0, "freq_per_day": 10},
            "student": {"avg_amount": 25.0, "freq_per_day": 1},
            "default": {"avg_amount": 100.0, "freq_per_day": 2}
        }
        
    def is_cold_start(self, user_history_count: int) -> bool:
        """
        Check if the user has enough transaction history.
        """
        return user_history_count < self.min_history_threshold
        
    def assign_cohort(self, user_metadata: dict) -> str:
        """
        Assign a user to a cohort based on KYC data or metadata.
        """
        if not user_metadata:
            return "default"
            
        age = user_metadata.get("age", 30)
        location = user_metadata.get("location", "urban").lower()
        account_type = user_metadata.get("account_type", "personal").lower()
        
        if account_type == "merchant":
            return "rural_merchant" if location == "rural" else "default"
        elif age < 25:
            return "student"
        elif location == "urban":
            return "urban_retail"
            
        return "default"

    def get_baseline(self, user_id: str, user_history_count: int, user_metadata: dict = None) -> dict:
        """
        Returns the appropriate baseline: personal if enough history, otherwise cohort.
        """
        if self.is_cold_start(user_history_count):
            cohort = self.assign_cohort(user_metadata)
            baseline = self.cohort_baselines.get(cohort)
            return {"type": "cohort", "cohort_name": cohort, "metrics": baseline}
        else:
            return {"type": "personal", "status": "sufficient_history"}
