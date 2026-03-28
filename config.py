"""
config.py
---------
Central configuration for HADIR system.
All settings in one place — database URL, TOTP parameters, app constants.

Think of this like your Excel config sheet: one source of truth
that every other file reads from.
"""

import os
from pathlib import Path

# ── Database ────────────────────────────────────────────────────────────────
# Railway provides DATABASE_URL automatically when you add PostgreSQL.
# Locally, falls back to your local PostgreSQL.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://hadir_user:hadir123@localhost:5432/hadir"
)

# Railway sometimes gives postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
SEED_DIR = BASE_DIR / "seed_data"

# ── TOTP / QR Token ────────────────────────────────────────────────────────
TOTP_INTERVAL_SECONDS = 300      # token rotates every 5 minutes
TOTP_SECRET = "HADIR_SMAN5_2026" # shared secret for TOTP generation
                                  # in production: use env var, not hardcoded

# ── School Constants ────────────────────────────────────────────────────────
DAYS_OF_WEEK = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]

# Period ranges per day (period 0 = cleaning, excluded)
PERIODS = {
    "Senin":  (1, 11),
    "Selasa": (1, 11),
    "Rabu":   (1, 11),
    "Kamis":  (1, 11),
    "Jumat":  (1, 7),
}

# ── Attendance Statuses ────────────────────────────────────────────────────
TEACHER_STATUSES = ["hadir", "tidak_hadir", "terlambat", "sakit", "izin"]
STUDENT_STATUSES = ["hadir", "tidak_hadir", "sakit", "izin", "alpa"]
