from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.doctor import Doctor, DoctorSchedule
from backend.app.repositories.base import BaseRepository


class DoctorRepository(BaseRepository[Doctor]):
    """Repository handling database operations for Doctor and DoctorSchedule entities."""

    def __init__(self, db: Session):
        super().__init__(db, Doctor)

    def get_by_user_id(self, user_id: int) -> Optional[Doctor]:
        """Fetch doctor record by underlying user account ID."""
        return self.db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def get_schedules(self, doctor_id: int) -> List[DoctorSchedule]:
        """Fetch all weekly availability schedules for a doctor."""
        return self.db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_id).all()

    def add_schedule(self, schedule: DoctorSchedule) -> DoctorSchedule:
        """Persist a new weekly schedule rule."""
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def get_schedule_by_day(self, doctor_id: int, day_of_week: str) -> Optional[DoctorSchedule]:
        """Fetch schedule rule for a specific day of the week."""
        return (
            self.db.query(DoctorSchedule)
            .filter(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.day_of_week.ilike(day_of_week)
            )
            .first()
        )
