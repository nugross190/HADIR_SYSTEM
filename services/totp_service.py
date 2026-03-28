"""
services/totp_service.py
-------------------------
TOTP (Time-based One-Time Password) service for staff presence verification.

How it works:
  1. The bell PC at school displays a 6-digit code
  2. The code changes every 5 minutes (configurable)
  3. Admin staff must enter the current code to start recording
  4. Server validates: correct code = staff is physically at school

This is NOT a cryptographic TOTP like Google Authenticator.
It's a simpler HMAC-based approach:
  - Shared secret (known to server + bell PC display app)
  - Current time window → deterministic 6-digit code
  - Server validates by computing the same code

The bell PC runs a simple display script that shows the current code.
No internet needed — both sides compute from time + secret.

Excel analogy: like a VLOOKUP where the lookup key is the current
time rounded to the nearest 5 minutes, and the table is generated
from a formula using a shared seed.
"""

import hmac
import hashlib
import struct
import time
from datetime import datetime, timezone

from config import TOTP_INTERVAL_SECONDS, TOTP_SECRET


def _get_time_window(timestamp: float = None) -> int:
    """
    Get the current time window number.
    
    Like dividing time into 5-minute buckets:
      00:00-04:59 = window 0
      05:00-09:59 = window 1
      10:00-14:59 = window 2
      ...
    """
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp) // TOTP_INTERVAL_SECONDS


def _generate_code(window: int) -> str:
    """
    Generate a 6-digit code for a given time window.
    
    Uses HMAC-SHA256 with the shared secret and window number
    to produce a deterministic but unpredictable code.
    """
    # Pack window number as 8 bytes (big-endian)
    window_bytes = struct.pack(">Q", window)

    # HMAC-SHA256
    secret_bytes = TOTP_SECRET.encode("utf-8")
    h = hmac.new(secret_bytes, window_bytes, hashlib.sha256).digest()

    # Dynamic truncation: use last 4 bits as offset
    offset = h[-1] & 0x0F
    code_int = struct.unpack(">I", h[offset:offset + 4])[0] & 0x7FFFFFFF

    # 6-digit code (zero-padded)
    return str(code_int % 1_000_000).zfill(6)


def get_current_code() -> dict:
    """
    Get the current TOTP code and its validity window.
    
    Returns:
        {
            "code": "847291",
            "valid_from": "2026-03-28T09:30:00+07:00",
            "valid_until": "2026-03-28T09:34:59+07:00",
            "seconds_remaining": 183
        }
    
    This is what the bell PC display app would call.
    """
    now = time.time()
    window = _get_time_window(now)
    code = _generate_code(window)

    window_start = window * TOTP_INTERVAL_SECONDS
    window_end = window_start + TOTP_INTERVAL_SECONDS - 1
    seconds_remaining = window_end - int(now) + 1

    return {
        "code": code,
        "valid_from": datetime.fromtimestamp(window_start, tz=timezone.utc).isoformat(),
        "valid_until": datetime.fromtimestamp(window_end, tz=timezone.utc).isoformat(),
        "seconds_remaining": seconds_remaining,
    }


def validate_code(entered_code: str) -> bool:
    """
    Validate a TOTP code entered by admin staff.
    
    Checks current window AND previous window (grace period).
    If the code changed 10 seconds ago and the admin was still typing,
    the previous window's code is still accepted.
    
    Returns True if valid, False if not.
    """
    now = time.time()
    current_window = _get_time_window(now)

    # Check current window
    if entered_code == _generate_code(current_window):
        return True

    # Check previous window (grace period for slow typers)
    if entered_code == _generate_code(current_window - 1):
        return True

    return False


def get_display_info() -> dict:
    """
    Full info for the bell PC display app.
    Shows current code prominently + countdown to next rotation.
    """
    info = get_current_code()
    now = time.time()
    window = _get_time_window(now)

    # Also show next code (for smooth transition on display)
    next_code = _generate_code(window + 1)
    info["next_code_preview"] = next_code

    return info
