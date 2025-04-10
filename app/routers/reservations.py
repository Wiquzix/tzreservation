from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.schemas import Reservation, ReservationCreate
from app.services import reservation_service

router = APIRouter()

@router.post("/", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate, db: AsyncSession = Depends(get_db)):
    return await reservation_service.create_reservation(db, reservation.model_dump())

@router.get("/", response_model=List[Reservation])
async def read_reservations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    reservations = await reservation_service.get_reservations(db, skip=skip, limit=limit)
    return reservations

@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    return await reservation_service.delete_reservation(db, reservation_id) 