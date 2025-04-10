import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import uuid
from app.main import app
from app.core.database import Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@test_db:5432/test_restaurant_db"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_db():
    """Очищаем базу данных перед каждым тестом"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    """Создаем тестовый клиент"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

def generate_unique_name(prefix: str = "Test Table") -> str:
    """Генерирует уникальное имя для столика"""
    return f"{prefix} {uuid.uuid4().hex[:8]}"

@pytest.mark.asyncio
async def test_create_table(client):
    table_data = {
        "name": generate_unique_name(),
        "seats": 4,
        "location": "Test Location"
    }
    response = await client.post("/tables/", json=table_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == table_data["name"]
    assert data["seats"] == table_data["seats"]
    assert data["location"] == table_data["location"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_tables(client):
    table_data = {
        "name": generate_unique_name(),
        "seats": 4,
        "location": "Test Location"
    }
    await client.post("/tables/", json=table_data)
    
    response = await client.get("/tables/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == table_data["name"]

@pytest.mark.asyncio
async def test_create_reservation(client):
    table_data = {
        "name": generate_unique_name(),
        "seats": 4,
        "location": "Test Location"
    }
    table_response = await client.post("/tables/", json=table_data)
    assert table_response.status_code == 200
    table_id = table_response.json()["id"]
    
    reservation_time = datetime.now() + timedelta(hours=1)
    reservation_data = {
        "customer_name": "Test Customer",
        "table_id": table_id,
        "reservation_time": reservation_time.isoformat(),
        "duration_minutes": 60
    }
    response = await client.post("/reservations/", json=reservation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == reservation_data["customer_name"]
    assert data["table_id"] == table_id

@pytest.mark.asyncio
async def test_reservation_conflict(client):
    table_data = {
        "name": generate_unique_name(),
        "seats": 4,
        "location": "Test Location"
    }
    table_response = await client.post("/tables/", json=table_data)
    assert table_response.status_code == 200
    table_id = table_response.json()["id"]
    
    reservation_time = datetime.now() + timedelta(hours=1)
    reservation_data = {
        "customer_name": "Test Customer 1",
        "table_id": table_id,
        "reservation_time": reservation_time.isoformat(),
        "duration_minutes": 60
    }
    response = await client.post("/reservations/", json=reservation_data)
    assert response.status_code == 200
    
    conflicting_reservation = {
        "customer_name": "Test Customer 2",
        "table_id": table_id,
        "reservation_time": (reservation_time + timedelta(minutes=30)).isoformat(),
        "duration_minutes": 60
    }
    response = await client.post("/reservations/", json=conflicting_reservation)
    assert response.status_code == 400
    assert "Столик уже забронирован" in response.json()["detail"] 