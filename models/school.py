"""
models/school.py
----------------
Class and Student — the school structure.

Class: 36 total (X-A through XII IPS-4), but 12th graders
       can be deactivated via is_active when they graduate.

Student: belongs to one Class. ~30-35 students per class.
         NIS (Nomor Induk Siswa) is the unique student ID.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)  # "X - A", "XI IPA - 1"
    grade_level = Column(Integer, nullable=False)             # 10, 11, 12
    is_active = Column(Boolean, default=True)

    # Relationships
    students = relationship("Student", back_populates="kelas")
    schedule_slots = relationship("ScheduleSlot", back_populates="kelas")

    def __repr__(self):
        return f"<Class(name='{self.name}', grade={self.grade_level})>"


class Student(Base):
    """
    NIS has 6 duplicate entries in source data (school admin typos).
    NISN also has 4 duplicates. So neither can be truly unique.
    
    We use auto-increment id as PK and add a unique constraint on
    (nis, class_id) — same NIS in different classes is the actual
    pattern of the duplicates.
    """
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("nis", "class_id", name="uq_student_nis_class"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nis = Column(String(20), nullable=False, index=True)
    nisn = Column(String(20), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    gender = Column(String(1), nullable=True)   # L or P
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    kelas = relationship("Class", back_populates="students")
    attendance_records = relationship("StudentAttendanceRecord", back_populates="student")

    def __repr__(self):
        return f"<Student(nis='{self.nis}', name='{self.name}')>"
