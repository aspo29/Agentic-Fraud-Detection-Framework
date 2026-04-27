import time
from typing import Optional
from .storage import get_latest_sim_event


def was_ported_within(phone_number: str, hours: int = 48) -> bool:
    """Mock carrier check: returns True if there is a sim_events entry within `hours` hours."""
    ts = get_latest_sim_event(phone_number)
    if not ts:
        return False
    now = int(time.time())
    return (now - ts) <= hours * 3600
