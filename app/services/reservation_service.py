from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from app.models.models import Reservation, Table
from fastapi import HTTPException

async def check_reservation_conflict(db: AsyncSession, table_id: int, reservation_time: datetime, duration_minutes: int) -> bool:
    query = select(Reservation).where(Reservation.table_id == table_id)
    result = await db.execute(query)
    existing_reservations = result.scalars().all()
    
    if reservation_time.tzinfo is not None:
        reservation_time = reservation_time.replace(tzinfo=None)
    
    new_start = reservation_time
    new_end = reservation_time + timedelta(minutes=duration_minutes)
    
    for reservation in existing_reservations:
        existing_start = reservation.reservation_time
        existing_end = existing_start + timedelta(minutes=reservation.duration_minutes)
        
        if (new_start < existing_end and new_end > existing_start):
            return True
    
    return False

async def create_reservation(db: AsyncSession, reservation: dict) -> Reservation:
    if reservation["reservation_time"].tzinfo is not None:
        reservation["reservation_time"] = reservation["reservation_time"].replace(tzinfo=None)
    
    table_query = select(Table).where(Table.id == reservation["table_id"])
    table_result = await db.execute(table_query)
    table = table_result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Столик не найден")
    
    if await check_reservation_conflict(
        db, 
        reservation["table_id"], 
        reservation["reservation_time"], 
        reservation["duration_minutes"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Столик уже забронирован на это время"
        )
    
    db_reservation = Reservation(**reservation)
    db.add(db_reservation)
    await db.commit()
    await db.refresh(db_reservation)
    
    await db.refresh(db_reservation, ["table"])
    return db_reservation

async def get_reservations(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(Reservation).options(joinedload(Reservation.table)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def delete_reservation(db: AsyncSession, reservation_id: int):
    query = select(Reservation).where(Reservation.id == reservation_id)
    result = await db.execute(query)
    reservation = result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    
    await db.delete(reservation)
    await db.commit()
    return reservation 