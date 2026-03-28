"""
routers/attendance.py
----------------------
Attendance recording endpoints — the core workflow.

POST /attendance/session/start       — start recording session (TOTP verify)
POST /attendance/session/complete    — mark session complete
GET  /attendance/session/{id}        — get session summary

GET  /attendance/schedule            — get today's schedule slots
GET  /attendance/class/{id}/students — get student roster for a class

POST /attendance/record              — record teacher + student attendance
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.attendance_service import (
    start_recording_session,
    complete_recording_session,
    get_today_schedule,
    get_class_students,
    record_attendance,
    get_recording_session_summary,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


# ── Request Models ──────────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    staff_id: int
    totp_code: str


class StudentStatusEntry(BaseModel):
    student_id: int
    status: str = "hadir"  # hadir, tidak_hadir, sakit, izin, alpa


class RecordAttendanceRequest(BaseModel):
    recording_session_id: int
    schedule_slot_id: int
    date: date
    teacher_status: str                     # hadir, tidak_hadir, terlambat, sakit, izin
    teacher_notes: Optional[str] = None
    student_statuses: list[StudentStatusEntry]


# ── Recording Session Endpoints ─────────────────────────────────────────────

@router.post("/session/start")
def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    """
    Start a recording session with TOTP verification.
    
    Admin enters the 6-digit code from the bell PC.
    If valid → session created, admin can start recording.
    If invalid → session logged as unverified, error returned.
    """
    try:
        result = start_recording_session(db, req.staff_id, req.totp_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/{session_id}/complete")
def complete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Mark a recording session as complete.
    Admin taps 'Done' when finished recording all classes.
    """
    try:
        result = complete_recording_session(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """
    Get summary of a recording session.
    Shows all classes recorded, teacher statuses, student counts.
    """
    try:
        result = get_recording_session_summary(db, session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Schedule & Roster Endpoints ─────────────────────────────────────────────

@router.get("/schedule")
def get_schedule(
    day: str = Query(..., description="Day name: Senin, Selasa, Rabu, Kamis, Jumat"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    db: Session = Depends(get_db),
):
    """
    Get schedule slots for a given day.
    
    Admin sees this when picking which class/slot to record.
    Shows teacher name, subject, period range for each slot.
    """
    return get_today_schedule(db, day, class_id)


@router.get("/class/{class_id}/students")
def get_students(class_id: int, db: Session = Depends(get_db)):
    """
    Get active student roster for a class.
    
    Admin sees this on page 2 — all students defaulted to 'hadir',
    they tap absent ones to flip status.
    """
    students = get_class_students(db, class_id)
    if not students:
        raise HTTPException(status_code=404, detail="No students found for this class")
    return students


# ── Record Attendance ───────────────────────────────────────────────────────

@router.post("/record")
def record(req: RecordAttendanceRequest, db: Session = Depends(get_db)):
    """
    Record attendance for one schedule slot.
    
    This is the main submit action — admin has:
    1. Selected the class and slot (page 1)
    2. Marked teacher status (page 1)
    3. Marked student statuses (page 2)
    4. Hit submit → this endpoint
    
    Creates one AttendanceSession with:
    - 1 TeacherAttendanceRecord
    - N StudentAttendanceRecords (one per student)
    """
    try:
        result = record_attendance(
            db=db,
            recording_session_id=req.recording_session_id,
            schedule_slot_id=req.schedule_slot_id,
            attendance_date=req.date,
            teacher_status=req.teacher_status,
            teacher_notes=req.teacher_notes,
            student_statuses=[
                {"student_id": s.student_id, "status": s.status}
                for s in req.student_statuses
            ],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
