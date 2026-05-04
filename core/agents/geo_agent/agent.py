'''│   ├── geo_agent/
│   │   ├── agent.py                # GeoAgent (main orchestrator)
│   │   ├── travel_detector.py     # haversine + impossible travel logic
│   │   ├── device_fingerprint.py  # hashing + device tracking
│   │   ├── redis_store.py         # last location + device cache
│   │   ├── models.py
│   │   └── __init__.py'''

from core.agents.geo_agent.traveler_detection import TravelDetector
from core.agents.geo_agent.device_fingerprint import DeviceFingerprint
from core.agents.geo_agent.redis_store import GeoRedisStore


class GeoAgent:

    def __init__(self, redis_client):
        self.store = GeoRedisStore(redis_client)

    async def process(self, payload: dict):

        # -----------------------------
        # VALIDATION
        # -----------------------------
        required_fields = ["user_id", "location", "device", "timestamp"]

        for field in required_fields:
            if field not in payload:
                return {
                    "agent": "geo_agent",
                    "error": f"missing_field: {field}"
                }

        user_id = payload["user_id"]
        current_loc = payload["location"]
        device = payload["device"]
        timestamp = float(payload["timestamp"])

        # -----------------------------
        # DEVICE FINGERPRINT
        # -----------------------------
        fingerprint = DeviceFingerprint.generate(device)

        known_devices = set(self.store.get_devices(user_id))

        if fingerprint in known_devices:
            device_risk = 0.05
            device_flag = "known_device"
        else:
            device_risk = 0.3
            device_flag = "new_device"
            self.store.add_device(user_id, fingerprint)

        # -----------------------------
        # LOCATION ANOMALY
        # -----------------------------
        last_loc = self.store.get_last_location(user_id)

        location_risk = 0.0
        travel_flag = None

        dist = 0.0
        time_diff_hours = 0.0

        if last_loc is not None:

            try:
                dist = TravelDetector.haversine(
                    float(last_loc["lat"]),
                    float(last_loc["lon"]),
                    float(current_loc["lat"]),
                    float(current_loc["lon"])
                )

                time_diff_hours = max(0.001, (timestamp - float(last_loc["timestamp"])) / 3600)
                speed= dist / time_diff_hours
                if speed > 700:
                      location_risk = 1.0
                      travel_flag = "impossible_travel"
                else:
                    location_risk = min(dist / 10000, 0.7)
                # -----------------------------
                # IMPORTANT FIX (NO TIME GATING BUG)
                # -----------------------------


            except Exception:
                dist = 0.0
                time_diff_hours = 0.0
                location_risk = 0.2
                travel_flag = None

        # -----------------------------
        # UPDATE LAST LOCATION
        # -----------------------------
        self.store.set_last_location(user_id, {
            "lat": float(current_loc["lat"]),
            "lon": float(current_loc["lon"]),
            "timestamp": timestamp
        })

        # -----------------------------
        # FINAL RISK SCORE
        # -----------------------------
        total_risk = min(
            0.6 * location_risk + 0.4 * device_risk,
            1.0
        )

        # -----------------------------
        # FLAGS
        # -----------------------------
        flags = []

        if travel_flag:
            flags.append(travel_flag)

        if device_flag == "new_device":
            flags.append("unknown_device")

        # -----------------------------
        # RESPONSE (ACCEPTANCE-COMPLIANT)
        # -----------------------------
        return {
            "agent": "geo_agent",
            "risk_score": total_risk,
            "location_risk": location_risk,
            "device_risk": device_risk,
            "flags": flags,

            # REQUIRED BY ACCEPTANCE CRITERIA
            "coordinates": {
                "lat": float(current_loc["lat"]),
                "lon": float(current_loc["lon"])
            },

            "fingerprint": fingerprint
        }