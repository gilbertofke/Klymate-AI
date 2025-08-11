"""
User Model

This module defines the User model for authentication and profile management.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """
    User model for authentication and profile management.
    
    Attributes:
        id: Unique identifier for the user
        firebase_uid: Firebase Authentication UID
        email: User's email address
        name: User's display name
        location: User's location for regional CO2 calculations
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    location = Column(String(255))

    # Relationships
    habits = relationship("UserHabit", back_populates="user", cascade="all, delete-orphan")
    created_habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert the User instance to a dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation of the User."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
