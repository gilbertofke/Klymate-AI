from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class HabitCategory(enum.Enum):
    TRANSPORT = "transport"
    ENERGY = "energy"
    FOOD = "food"
    WASTE = "waste"
    OTHER = "other"

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(Enum(HabitCategory))
    name = Column(String(255))
    description = Column(String(500))
    carbon_impact = Column(Float)  # Estimated CO2 impact in kg
    frequency = Column(String(50))  # daily, weekly, monthly
    
    # Relationships
    user = relationship("User", back_populates="habits")
    footprints = relationship("CarbonFootprint", back_populates="habit")
