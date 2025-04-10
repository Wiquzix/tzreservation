from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.schemas import Table, TableCreate
from app.services import table_service

router = APIRouter()

@router.post("/", response_model=Table)
async def create_table(table: TableCreate, db: AsyncSession = Depends(get_db)):
    return await table_service.create_table(db, table.model_dump())

@router.get("/", response_model=List[Table])
async def read_tables(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    tables = await table_service.get_tables(db, skip=skip, limit=limit)
    return tables

@router.delete("/{table_id}")
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    return await table_service.delete_table(db, table_id) 