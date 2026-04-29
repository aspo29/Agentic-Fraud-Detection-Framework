from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    lat: float
    lon: float
    country: str

    # optional but highly useful in fraud systems
    city: Optional[str] = None
    accuracy_meters: Optional[float] = None
    timestamp: Optional[int] = None

@dataclass
class DeviceInfo:
    user_agent: str
    os: str
    screen: str
    ip: str

      # optional enhancements for better fingerprinting
    language: Optional[str] = None
    timezone: Optional[str] = None
    device_id: Optional[str] = None