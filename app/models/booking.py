from datetime import date, datetime
from sqlalchemy import Column, Integer, ForeignKey, Date, Float, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(String, default="confirmed", nullable=False)  # confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    room = relationship("Room")
    customer = relationship("Customer")
