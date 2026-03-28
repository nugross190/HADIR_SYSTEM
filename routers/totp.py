"""
routers/totp.py
----------------
TOTP token endpoints.

GET  /totp/current    — get current code (for bell PC display)
GET  /totp/display    — full display info with countdown + next preview
POST /totp/validate   — check if entered code is valid
"""

from fastapi import APIRouter
from pydantic import BaseModel

from services.totp_service import get_current_code, validate_code, get_display_info

router = APIRouter(prefix="/totp", tags=["totp"])


class ValidateRequest(BaseModel):
    code: str


@router.get("/current")
def current_code():
    """
    Get the current TOTP code.
    
    This endpoint would be called by the bell PC display app
    to show the current code on screen.
    """
    return get_current_code()


@router.get("/display")
def display_info():
    """
    Full display info for the bell PC.
    Includes current code, countdown, and next code preview.
    """
    return get_display_info()


@router.post("/validate")
def validate(req: ValidateRequest):
    """
    Validate a TOTP code.
    
    Accepts current window + previous window (grace period).
    Returns whether the code is valid.
    """
    is_valid = validate_code(req.code)
    return {"code": req.code, "valid": is_valid}
