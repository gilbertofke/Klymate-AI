from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class CarbonFootprint(Base, TimestampMixin):
    __tablename__ = "carbon_footprints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    habit_id = Column(Integer, ForeignKey("habits.id"))
    date = Column(Date)
    carbon_value = Column(Float)  # CO2 in kg
    notes = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="footprints")
    habit = relationship("Habit", back_populates="footprints")
