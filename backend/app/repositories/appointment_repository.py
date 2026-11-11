from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """Repository managing database persistence and conflict checks for Appointments."""

    def __init__(self, db: Session):
        super().__init__(db, Appointment)

    def check_doctor_conflict(self, doctor_id: int, appointment_date: date, appointment_time: str) -> bool:
        """Returns True if doctor already has an active (non-cancelled) appointment in this time slot."""
        existing = (
            self.db.query(Appointment)
            .filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.appointment_time == appointment_time,
                Appointment.status != AppointmentStatus.CANCELLED.value,
            )
            .first()
        )
        return existing is not None

    def check_patient_conflict(self, patient_id: int, appointment_date: date, appointment_time: str) -> bool:
        """Returns True if patient already has an overlapping active appointment in this time slot."""
        existing = (
            self.db.query(Appointment)
            .filter(
                Appointment.patient_id == patient_id,
                Appointment.appointment_date == appointment_date,
                Appointment.appointment_time == appointment_time,
                Appointment.status != AppointmentStatus.CANCELLED.value,
            )
            .first()
        )
        return existing is not None

    def get_by_date(self, target_date: date) -> List[Appointment]:
        """Fetch all appointments on a given date."""
        return self.db.query(Appointment).filter(Appointment.appointment_date == target_date).all()

    def get_by_doctor_and_date(self, doctor_id: int, target_date: date) -> List[Appointment]:
        """Fetch all appointments for a specific doctor on a given date."""
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == target_date,
            )
            .all()
        )
