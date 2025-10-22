from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)  # e.g., cash, card
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    booking = relationship("Booking")
