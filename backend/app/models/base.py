"""
Base Model Classes

This module provides base model classes with common fields and utilities
for all database models in the Klymate AI application.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel as PydanticBaseModel

# SQLAlchemy Base
Base = declarative_base()


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model class with common fields."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + 's'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Mixin for audit trail fields."""
    
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    def set_created_by(self, user_id: str):
        """Set created by user."""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: str):
        """Set updated by user."""
        self.updated_by = user_id


# Pydantic Base Models for API schemas
class BaseSchema(PydanticBaseModel):
    """Base Pydantic model for API schemas."""
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


class BaseResponseSchema(TimestampSchema):
    """Base response schema with ID and timestamps."""
    
    id: int
    created_at: datetime
    updated_at: datetime


class BaseCreateSchema(BaseSchema):
    """Base schema for create operations."""
    pass


class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations."""
    pass