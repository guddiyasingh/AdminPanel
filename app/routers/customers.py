from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.db import get_session
from app.models.customer import Customer
from app.schemas import CustomerCreate, CustomerOut

router = APIRouter()

@router.post("/", response_model=CustomerOut)
async def create_customer(customer_in: CustomerCreate, session: AsyncSession = Depends(get_session)):
    existing = (await session.execute(select(Customer).where(Customer.email == customer_in.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    customer = Customer(**customer_in.model_dump())
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer

@router.get("/", response_model=List[CustomerOut])
async def list_customers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Customer))
    return result.scalars().all()

@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int, session: AsyncSession = Depends(get_session)):
    customer = (await session.execute(select(Customer).where(Customer.id == customer_id))).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, customer_in: CustomerCreate, session: AsyncSession = Depends(get_session)):
    customer = (await session.execute(select(Customer).where(Customer.id == customer_id))).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    for k, v in customer_in.model_dump().items():
        setattr(customer, k, v)
    await session.commit()
    await session.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, session: AsyncSession = Depends(get_session)):
    customer = (await session.execute(select(Customer).where(Customer.id == customer_id))).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    await session.delete(customer)
    await session.commit()
    return {"ok": True}
