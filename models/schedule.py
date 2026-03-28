"""
models/schedule.py
------------------
ScheduleSlot — the weekly timetable template.

Each slot = one teacher teaching one class for a block of consecutive periods.
From your schedule.json: 795 slots total.

Example: kode_guru=9, kelas="X - A", hari="Senin", period_start=3, period_end=5
         means teacher 9 teaches X-A on Monday for periods 3, 4, 5.

The sub_kode field stores the raw code from the schedule (e.g. "13.1")
while teacher_id FK points to the parent teacher (kode 13).
This preserves the original data while maintaining clean relationships.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)   # Senin, Selasa, ...
    period_start = Column(Integer, nullable=False)      # 1-11
    period_end = Column(Integer, nullable=False)         # 1-11
    subject = Column(String(100), nullable=True)         # filled from mata_pelajaran
    sub_kode = Column(String(10), nullable=True)         # raw code: "13", "13.1"

    # Relationships
    teacher = relationship("Teacher", back_populates="schedule_slots")
    kelas = relationship("Class", back_populates="schedule_slots")
    attendance_sessions = relationship("AttendanceSession", back_populates="schedule_slot")

    def __repr__(self):
        return (
            f"<ScheduleSlot(class={self.class_id}, teacher={self.teacher_id}, "
            f"{self.day_of_week} p{self.period_start}-{self.period_end})>"
        )
