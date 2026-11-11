from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from backend.app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    address = Column(String(255), nullable=True)
    emergency_contact = Column(String(50), nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
