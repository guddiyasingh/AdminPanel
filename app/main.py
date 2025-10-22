from fastapi import FastAPI
from app.core.db import init_db
from app.routers import auth, rooms, customers, bookings, payments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hotel Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
