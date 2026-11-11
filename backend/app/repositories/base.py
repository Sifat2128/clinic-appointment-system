from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from backend.app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic Repository implementing standard database CRUD operations."""

    def __init__(self, db: Session, model_class: Type[ModelType]):
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Fetch entity by primary key."""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Fetch all entities with pagination."""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()

    def create(self, entity: ModelType) -> ModelType:
        """Persist a new entity instance."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, id: int, data: dict[str, Any]) -> Optional[ModelType]:
        """Update fields on existing entity."""
        entity = self.get_by_id(id)
        if not entity:
            return None
        for key, value in data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, id: int) -> bool:
        """Remove entity by primary key."""
        entity = self.get_by_id(id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
