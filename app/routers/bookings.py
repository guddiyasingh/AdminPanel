from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import date
from typing import List
from app.core.db import get_session
from app.models.booking import Booking
from app.models.room import Room
from app.models.customer import Customer
from app.schemas import BookingCreate, BookingOut

router = APIRouter()

def intervals_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return not (a_end <= b_start or a_start >= b_end)

@router.post("/", response_model=BookingOut)
async def create_booking(booking_in: BookingCreate, session: AsyncSession = Depends(get_session)):
    if booking_in.check_out <= booking_in.check_in:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")
    room = (await session.execute(select(Room).where(Room.id == booking_in.room_id))).scalar_one_or_none()
    customer = (await session.execute(select(Customer).where(Customer.id == booking_in.customer_id))).scalar_one_or_none()
    if not room or not customer:
        raise HTTPException(status_code=404, detail="Room or Customer not found")
    overlapping = (await session.execute(select(Booking).where(Booking.room_id == booking_in.room_id, ~or_(Booking.check_out <= booking_in.check_in, Booking.check_in >= booking_in.check_out), Booking.status == "confirmed"))).scalars().first()
    if overlapping:
        raise HTTPException(status_code=400, detail="Room not available for the selected dates")
    booking = Booking(**booking_in.model_dump())
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking

@router.get("/", response_model=List[BookingOut])
async def list_bookings(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Booking))
    return result.scalars().all()

@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, session: AsyncSession = Depends(get_session)):
    booking = (await session.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=BookingOut)
async def update_booking(booking_id: int, booking_in: BookingCreate, session: AsyncSession = Depends(get_session)):
    booking = (await session.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # check availability if room or dates changed
    if (booking.room_id != booking_in.room_id) or (booking.check_in != booking_in.check_in) or (booking.check_out != booking_in.check_out):
        overlapping = (await session.execute(select(Booking).where(Booking.room_id == booking_in.room_id, Booking.id != booking_id, ~or_(Booking.check_out <= booking_in.check_in, Booking.check_in >= booking_in.check_out), Booking.status == "confirmed"))).scalars().first()
        if overlapping:
            raise HTTPException(status_code=400, detail="Room not available for the selected dates")
    for k, v in booking_in.model_dump().items():
        setattr(booking, k, v)
    await session.commit()
    await session.refresh(booking)
    return booking

@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, session: AsyncSession = Depends(get_session)):
    booking = (await session.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    await session.delete(booking)
    await session.commit()
    return {"ok": True}
