from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    specialization = Column(String(100), nullable=False, index=True)
    consultation_fee = Column(Float, nullable=False, default=1000.0)
    phone = Column(String(50), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)

    user = relationship("User", backref="doctor_profile")
    schedules = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String(10), nullable=False)   # "09:00"
    end_time = Column(String(10), nullable=False)     # "13:00"
    slot_duration_minutes = Column(Integer, default=30, nullable=False)
    max_patients = Column(Integer, default=1, nullable=False)

    doctor = relationship("Doctor", back_populates="schedules")
