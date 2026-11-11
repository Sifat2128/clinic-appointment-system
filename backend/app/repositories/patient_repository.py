from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.patient import Patient
from backend.app.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repository handling database operations for Patient entities."""

    def __init__(self, db: Session):
        super().__init__(db, Patient)

    def search(self, query: str) -> List[Patient]:
        """Search patients by name or phone substring."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Patient)
            .filter(
                or_(
                    Patient.full_name.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern),
                )
            )
            .all()
        )
