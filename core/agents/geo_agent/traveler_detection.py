import math


class TravelDetector:

    EARTH_RADIUS_KM = 6371

    # VALIDATION HELPERS
    @staticmethod
    def _validate_coords(lat, lon) -> bool:
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return False

        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False

        return True

    # HAVERSINE DISTANCE
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Distance between two Earth coordinates (km)
        """

        # validation (important for Kafka input safety)
        if not TravelDetector._validate_coords(lat1, lon1):
            return 0.0
        if not TravelDetector._validate_coords(lat2, lon2):
            return 0.0

        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)

        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2 +
            math.cos(phi1) *
            math.cos(phi2) *
            math.sin(dlambda / 2) ** 2
        )

        # clamp for floating-point safety
        a = min(1.0, max(0.0, a))

        return 2 * TravelDetector.EARTH_RADIUS_KM * math.asin(math.sqrt(a))

    # IMPOSSIBLE TRAVEL DETECTION
    @staticmethod
    def is_impossible_travel(dist_km: float, time_hours: float) -> bool:

        try:
            dist_km = float(dist_km)
            time_hours = float(time_hours)
        except (TypeError, ValueError):
            return True  # treat invalid data as suspicious

        if time_hours <= 0:
            return True

        if dist_km < 0:
            return True

        speed = dist_km / time_hours

        # FRAUD THRESHOLD (tunable)
   
        return speed > 700  ### acceptance criteria::commercial jets are around 800-900 km/h, so this is a high threshold for fraud detection