# rules.py
class VelocityRules:
    """
    Pure fraud logic (no Redis, no Kafka).
    """

    HIGH_RISK_THRESHOLD = 5 # transaction greater than 5 in the sliding window of 2 minutes is considered high risk
    LOW_RISK_THRESHOLD = 1   # transaction less than or equal to 1 in the sliding window is considered low risk

    @staticmethod
    def compute_score(window_count: int) -> float:
        if window_count >= VelocityRules.HIGH_RISK_THRESHOLD:
            return 0.9

        if window_count <= VelocityRules.LOW_RISK_THRESHOLD:
            return 0.1

        return min(1.0, window_count / VelocityRules.HIGH_RISK_THRESHOLD)