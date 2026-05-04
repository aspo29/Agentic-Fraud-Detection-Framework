import hashlib
import json


class DeviceFingerprint:

    @staticmethod
    def generate(device: dict) -> str:
        """
        Deterministic + normalized + collision-safe fingerprint
        """

        normalized = {
            "user_agent": device.get("user_agent", "").strip().lower(),
            "os": device.get("os", "").strip().lower(),
            "screen": device.get("screen", "").strip(),
            "ip_subnet": DeviceFingerprint._get_ip_subnet(device.get("ip", ""))
        }

        raw = json.dumps(normalized, sort_keys=True)

        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def _get_ip_subnet(ip: str) -> str:
        """
        Basic IPv4 / IPv6-safe approximation
        """
        if ":" in ip:  # IPv6
            return ip.split(":")[0:4][0] if ip else ""
        else:  # IPv4
            return ".".join(ip.split(".")[0:2]) if ip else ""