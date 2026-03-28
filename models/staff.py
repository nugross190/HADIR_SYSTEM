"""
models/staff.py
---------------
Admin staff who physically walk to classrooms and record attendance.
These are your 3 administration staff.

Staff has a pin_hash for login — no complex auth needed,
just a simple PIN since the TOTP already proves physical presence.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    pin_hash = Column(String(255), nullable=False)  # hashed 4-6 digit PIN
    role = Column(String(20), default="admin")       # admin | superadmin
    is_active = Column(Boolean, default=True)

    # Relationships
    recording_sessions = relationship("RecordingSession", back_populates="staff")

    def __repr__(self):
        return f"<Staff(id={self.id}, name='{self.name}', role='{self.role}')>"
