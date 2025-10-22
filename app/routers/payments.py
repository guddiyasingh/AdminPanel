from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.db import get_session
from app.models.payment import Payment
from app.models.booking import Booking
from app.schemas import PaymentCreate, PaymentOut

router = APIRouter()

@router.post("/", response_model=PaymentOut)
async def create_payment(payment_in: PaymentCreate, session: AsyncSession = Depends(get_session)):
    booking = (await session.execute(select(Booking).where(Booking.id == payment_in.booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    payment = Payment(**payment_in.model_dump())
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment

@router.get("/", response_model=List[PaymentOut])
async def list_payments(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Payment))
    return result.scalars().all()

@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(payment_id: int, session: AsyncSession = Depends(get_session)):
    payment = (await session.execute(select(Payment).where(Payment.id == payment_id))).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
