from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Table
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

async def create_table(db: AsyncSession, table: dict) -> Table:
    try:
        db_table = Table(**table)
        db.add(db_table)
        await db.commit()
        await db.refresh(db_table)
        return db_table
    except IntegrityError as e:
        await db.rollback()
        if "ix_tables_name" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Столик с названием '{table['name']}' уже существует"
            )
        raise HTTPException(
            status_code=400,
            detail="Ошибка при создании столика"
        )

async def get_tables(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(Table).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def delete_table(db: AsyncSession, table_id: int):
    query = select(Table).where(Table.id == table_id)
    result = await db.execute(query)
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Столик не найден")
    
    await db.delete(table)
    await db.commit()
    return table 