"""
routers/totp.py
----------------
TOTP token endpoints.

GET  /totp/current?key=xxx    — get current code (requires display key)
GET  /totp/display?key=xxx    — full display info (requires display key)
POST /totp/validate           — check if entered code is valid (open — admin flow)
"""

import os

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.totp_service import get_current_code, validate_code, get_display_info

router = APIRouter(prefix="/totp", tags=["totp"])

DISPLAY_KEY = os.environ.get("DISPLAY_KEY", "hadir-display-2026")


def _check_display_key(key: str = Query(None)):
    if not key or key != DISPLAY_KEY:
        raise HTTPException(status_code=403, detail="Akses ditolak")


class ValidateRequest(BaseModel):
    code: str


@router.get("/current")
def current_code(key: str = Query(None)):
    """Get current TOTP code. Requires display key."""
    _check_display_key(key)
    return get_current_code()


@router.get("/display")
def display_info(key: str = Query(None)):
    """Full display info for bell PC. Requires display key."""
    _check_display_key(key)
    return get_display_info()


@router.post("/validate")
def validate(req: ValidateRequest):
    """Validate a TOTP code. Open — used during admin attendance flow."""
    is_valid = validate_code(req.code)
    return {"code": req.code, "valid": is_valid}