"""
models/attendance.py
--------------------
The attendance recording chain:

  RecordingSession  (staff proves presence via TOTP, starts recording)
       |
       ├── AttendanceSession  (one per schedule slot per date)
       |        |
       |        ├── TeacherAttendanceRecord  (1:1 — was teacher there?)
       |        └── StudentAttendanceRecord  (1:N — each student's status)
       |
       └── AttendanceSession  (next slot...)
            ...

QRToken stores the rotating TOTP codes for validation.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class QRToken(Base):
    """
    Rotating TOTP-style tokens displayed on the school's bell PC.
    Staff must enter the current token to prove physical presence.
    """
    __tablename__ = "qr_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_value = Column(String(10), nullable=False, index=True)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RecordingSession(Base):
    """
    A recording session = one admin staff sitting down to record attendance.
    
    This is the accountability wrapper. Your boss sees:
    "Admin A verified TOTP at 09:32, recorded 8 classes, finished at 09:55"
    
    If Admin C has zero RecordingSessions today — that's the report.
    """
    __tablename__ = "recording_sessions"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)  # NULL until they finish
    totp_code_entered = Column(String(10), nullable=True)
    totp_verified = Column(Boolean, default=False)

    # Relationships
    staff = relationship("Staff", back_populates="recording_sessions")
    attendance_sessions = relationship(
        "AttendanceSession", back_populates="recording_session"
    )

    def __repr__(self):
        status = "verified" if self.totp_verified else "unverified"
        return f"<RecordingSession(id={self.id}, staff={self.staff_id}, {status})>"


class AttendanceSession(Base):
    """
    One recording for one schedule slot on one date.
    
    The admin walks into X-A, asks about Pak Budi's period 3-5 block.
    This creates one AttendanceSession linked to that ScheduleSlot + today's date.
    
    Parents both the teacher record and all student records for that slot.
    """
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    schedule_slot_id = Column(
        Integer, ForeignKey("schedule_slots.id"), nullable=False
    )
    recording_session_id = Column(
        Integer, ForeignKey("recording_sessions.id"), nullable=False
    )
    date = Column(Date, nullable=False, index=True)
    recorded_at = Column(DateTime, server_default=func.now())

    # Relationships
    schedule_slot = relationship("ScheduleSlot", back_populates="attendance_sessions")
    recording_session = relationship(
        "RecordingSession", back_populates="attendance_sessions"
    )
    teacher_record = relationship(
        "TeacherAttendanceRecord",
        back_populates="attendance_session",
        uselist=False,  # 1:1 relationship
    )
    student_records = relationship(
        "StudentAttendanceRecord", back_populates="attendance_session"
    )

    def __repr__(self):
        return (
            f"<AttendanceSession(slot={self.schedule_slot_id}, "
            f"date={self.date})>"
        )


class TeacherAttendanceRecord(Base):
    """
    Was the teacher physically present for this schedule slot?
    One record per AttendanceSession.
    
    Statuses: hadir, tidak_hadir, terlambat, sakit, izin
    """
    __tablename__ = "teacher_attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    attendance_session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.id"),
        nullable=False,
        unique=True,  # enforces 1:1
    )
    status = Column(String(20), nullable=False, default="hadir")
    notes = Column(Text, nullable=True)  # e.g. "left after 20 minutes"

    # Relationships
    attendance_session = relationship(
        "AttendanceSession", back_populates="teacher_record"
    )

    def __repr__(self):
        return f"<TeacherRecord(session={self.attendance_session_id}, status='{self.status}')>"


class StudentAttendanceRecord(Base):
    """
    Was this student present during this schedule slot?
    N records per AttendanceSession (one per student in the class).
    
    Statuses: hadir, tidak_hadir, sakit, izin, alpa
    """
    __tablename__ = "student_attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    attendance_session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.id"),
        nullable=False,
    )
    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False,
    )
    status = Column(String(20), nullable=False, default="hadir")

    # Relationships
    attendance_session = relationship(
        "AttendanceSession", back_populates="student_records"
    )
    student = relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<StudentRecord(student={self.student_id}, status='{self.status}')>"
