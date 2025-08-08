from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    location = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    habits = relationship("Habit", back_populates="user")
    footprints = relationship("CarbonFootprint", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
