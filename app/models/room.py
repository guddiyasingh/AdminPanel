from sqlalchemy import Column, Integer, String, Boolean, Float
from app.core.db import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # e.g., single, double, suite
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
