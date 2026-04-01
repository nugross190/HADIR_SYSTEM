"""
routers/auth.py
----------------
Authentication endpoints.

POST /auth/login         — verify staff PIN (admin, headmaster)
POST /auth/owner-login   — verify owner/administrator PIN (env var based)
GET  /auth/staff         — list active staff (for login screen)
POST /auth/add-staff     — add a new staff account (for seeding missing accounts)
"""

import os

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from database import get_db
from services.auth_service import verify_staff_pin, list_staff
from models import Staff

router = APIRouter(prefix="/auth", tags=["auth"])

# Owner PIN — set in Railway env vars. Fallback for local dev.
OWNER_PIN = os.environ.get("OWNER_PIN", "admin2026")


class LoginRequest(BaseModel):
    staff_id: int
    pin: str


class OwnerLoginRequest(BaseModel):
    pin: str


class AddStaffRequest(BaseModel):
    name: str
    pin: str
    role: str = "admin"


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


@router.post("/add-staff")
def add_staff(
    req: AddStaffRequest,
    owner_pin: str = Query(..., alias="key"),
    db: Session = Depends(get_db),
):
    """
    Add a new staff account. Requires owner key for security.
    
    Usage: POST /auth/add-staff?key=YOUR_OWNER_PIN
    Body: {"name": "Kepala Sekolah", "pin": "1111", "role": "headmaster"}
    
    Safe to call multiple times — skips if name already exists.
    """
    if owner_pin != OWNER_PIN:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    if req.role not in ("admin", "headmaster"):
        raise HTTPException(status_code=400, detail="Role harus admin atau headmaster")

    existing = db.query(Staff).filter(Staff.name == req.name).first()
    if existing:
        return {"status": "already exists", "staff_id": existing.id, "name": existing.name, "role": existing.role}

    staff = Staff(
        name=req.name.strip(),
        pin_hash=bcrypt.hash(req.pin),
        role=req.role,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)

    return {"status": "created", "staff_id": staff.id, "name": staff.name, "role": staff.role}