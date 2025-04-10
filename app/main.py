from fastapi import FastAPI
from app.routers import tables, reservations
from app.core.database import engine, Base
import asyncio
from sqlalchemy.exc import OperationalError
import logging
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Restaurant Reservation API",
    description="API for restaurant table reservations",
)

async def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Миграции успешно применены")
    except Exception as e:
        logger.error(f"Ошибка при применении миграций: {e}")
        raise

async def init_db():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("База данных успешно инициализирована")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Попытка подключения к базе данных {attempt + 1}/{max_retries} не удалась: {e}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Не удалось подключиться к базе данных после всех попыток")
                raise

@app.on_event("startup")
async def startup():
    await init_db()
    await run_migrations()

app.include_router(tables.router, prefix="/tables", tags=["tables"])
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"]) 