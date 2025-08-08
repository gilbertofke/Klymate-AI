from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Badge(Base, TimestampMixin):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(500))
    criteria = Column(String(500))  # JSON string of achievement criteria
    image_url = Column(String(255))
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base, TimestampMixin):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_date = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
