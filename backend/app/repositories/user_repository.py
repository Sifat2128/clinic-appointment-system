from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database access for User entities."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by exact email address."""
        return self.db.query(User).filter(User.email == email).first()
