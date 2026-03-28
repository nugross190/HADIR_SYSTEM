"""
models/teacher.py
-----------------
Teachers from Kode Guru sheet.
67 teachers, each with a unique kode.

Sub-codes (13.1, 26.1 etc) are handled at the ScheduleSlot level —
the Teacher table stores the parent teacher only.
The sub_kode in schedule maps back to parent via integer part.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    nip = Column(String(30), nullable=True)   # some teachers don't have NIP
    status = Column(String(20), nullable=True) # PNS, Honorer, etc
    is_active = Column(Boolean, default=True)

    # Relationships
    schedule_slots = relationship("ScheduleSlot", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher(kode={self.kode}, name='{self.name}')>"
