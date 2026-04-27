import sqlite3
import threading
import time
from typing import List, Tuple, Optional

import os

DB_PATH = os.getenv("GIBL_DB_PATH", "gibl_app.db")
_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS flagged_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            transaction_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            ts INTEGER NOT NULL,
            UNIQUE(user_id, transaction_id, reason)
        )
        """
        )
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS sim_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            port_ts INTEGER NOT NULL
        )
        """
        )
        conn.commit()
        conn.close()


def flag_account(user_id: str, transaction_id: str, reason: str, ts: Optional[int] = None) -> None:
    ts = ts or int(time.time())
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT OR IGNORE INTO flagged_accounts (user_id, transaction_id, reason, ts) VALUES (?, ?, ?, ?)",
                (user_id, transaction_id, reason, ts),
            )
            conn.commit()
        finally:
            conn.close()


def get_flagged_accounts() -> List[sqlite3.Row]:
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, transaction_id, reason, ts FROM flagged_accounts ORDER BY ts DESC")
        rows = cur.fetchall()
        conn.close()
        return rows


def add_sim_event(phone_number: str, port_ts: int) -> None:
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO sim_events (phone_number, port_ts) VALUES (?, ?)", (phone_number, port_ts))
        conn.commit()
        conn.close()


def get_latest_sim_event(phone_number: str) -> Optional[int]:
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT port_ts FROM sim_events WHERE phone_number = ? ORDER BY port_ts DESC LIMIT 1", (phone_number,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
