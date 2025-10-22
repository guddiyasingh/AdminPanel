from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import date
from app.core.db import get_session
from app.models.room import Room
from app.models.booking import Booking
from app.schemas import RoomCreate, RoomOut
from typing import List

router = APIRouter()

@router.post("/", response_model=RoomOut)
async def create_room(room_in: RoomCreate, session: AsyncSession = Depends(get_session)):
    room = Room(**room_in.model_dump())
    session.add(room)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    await session.refresh(room)
    return room

@router.get("/", response_model=List[RoomOut])
async def list_rooms(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Room))
    return result.scalars().all()

@router.get("/{room_id}", response_model=RoomOut)
async def get_room(room_id: int, session: AsyncSession = Depends(get_session)):
    room = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomOut)
async def update_room(room_id: int, room_in: RoomCreate, session: AsyncSession = Depends(get_session)):
    room = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    for k, v in room_in.model_dump().items():
        setattr(room, k, v)
    await session.commit()
    await session.refresh(room)
    return room

@router.delete("/{room_id}")
async def delete_room(room_id: int, session: AsyncSession = Depends(get_session)):
    room = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    await session.delete(room)
    await session.commit()
    return {"ok": True}

@router.get("/available", response_model=List[RoomOut])
async def available_rooms(check_in: date = Query(...), check_out: date = Query(...), session: AsyncSession = Depends(get_session)):
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")
    # Rooms where no booking overlaps the requested interval
    overlapping = select(Booking.room_id).where(~or_(Booking.check_out <= check_in, Booking.check_in >= check_out), Booking.status == "confirmed")
    result = await session.execute(select(Room).where(~Room.id.in_(overlapping)))
    return result.scalars().all()
