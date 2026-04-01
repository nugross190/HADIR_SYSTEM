"""
routers/auth.py
----------------
Staff authentication endpoints.

POST /auth/login         — verify staff PIN
POST /auth/owner-login   — verify owner/administrator PIN
GET  /auth/staff         — list active staff (for login screen)
"""

import os

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.auth_service import verify_staff_pin, list_staff

router = APIRouter(prefix="/auth", tags=["auth"])

# Owner PIN — set in Railway env vars. Fallback for local dev only.
OWNER_PIN = os.environ.get("OWNER_PIN", "admin2026")


class LoginRequest(BaseModel):
    staff_id: int
    pin: str


class OwnerLoginRequest(BaseModel):
    pin: str


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Verify staff PIN. Returns staff info on success."""
    try:
        result = verify_staff_pin(db, req.staff_id, req.pin)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/owner-login")
def owner_login(req: OwnerLoginRequest):
    """Verify owner/administrator PIN. Not tied to a staff account."""
    if req.pin != OWNER_PIN:
        raise HTTPException(status_code=401, detail="PIN salah")
    return {"role": "owner", "name": "Administrator"}


@router.get("/staff")
def get_staff_list(
    role: str = Query(None, description="Filter by role: admin, headmaster"),
    db: Session = Depends(get_db),
):
    """List all active staff for the login screen, optionally filtered by role."""
    return list_staff(db, role=role)
