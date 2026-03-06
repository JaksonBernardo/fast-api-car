import os
import pytest
import pytest_asyncio
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Set environment variables BEFORE importing any application code
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'test'
os.environ['DB_PASSWORD'] = 'test'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'test_db'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['JWT_SECRET_KEY'] = 'testsecretkey123456789'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_EXPIRATION_MINUTES'] = '30'

from car_api.app import app
from car_api.core.database import get_session
from car_api.core.security import get_password_hash
from car_api.models import Base, User, Brand, Car
from car_api.models.cars import FuelType, TransmissionType


@pytest_asyncio.fixture
async def session():
    """
    Create an in-memory SQLite database for testing.
    Creates all tables before yielding the session and drops them after.
    """
    engine = create_async_engine(
        url='sqlite+aiosqlite:///:memory:',
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(session: AsyncSession):
    """
    Create a test client with overridden database session dependency.
    """
    def get_session_override():
        return session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_data():
    """Default user data for testing."""
    return {
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@test.com'
    }


@pytest_asyncio.fixture
async def user(session: AsyncSession, user_data: dict) -> User:
    """
    Create and persist a test user in the database.
    """
    hashed_password = get_password_hash(user_data["password"])

    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        password=hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def second_user_data():
    """Second user data for testing."""
    return {
        'username': 'seconduser',
        'password': 'password456',
        'email': 'second@test.com'
    }


@pytest_asyncio.fixture
async def second_user(session: AsyncSession, second_user_data: dict) -> User:
    """
    Create and persist a second test user in the database.
    """
    hashed_password = get_password_hash(second_user_data["password"])

    db_user = User(
        username=second_user_data["username"],
        email=second_user_data["email"],
        password=hashed_password
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@pytest_asyncio.fixture
async def brand_data():
    """Default brand data for testing."""
    return {
        'name': 'Toyota',
        'description': 'Japanese car manufacturer',
        'is_active': True
    }


@pytest_asyncio.fixture
async def brand(session: AsyncSession, brand_data: dict, user: User) -> Brand:
    """
    Create and persist a test brand in the database.
    """
    db_brand = Brand(
        name=brand_data["name"],
        description=brand_data["description"],
        is_active=brand_data["is_active"]
    )

    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
async def second_brand_data():
    """Second brand data for testing."""
    return {
        'name': 'Honda',
        'description': 'Another Japanese car manufacturer',
        'is_active': True
    }


@pytest_asyncio.fixture
async def second_brand(session: AsyncSession, second_brand_data: dict) -> Brand:
    """
    Create and persist a second test brand in the database.
    """
    db_brand = Brand(
        name=second_brand_data["name"],
        description=second_brand_data["description"],
        is_active=second_brand_data["is_active"]
    )

    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
async def inactive_brand_data():
    """Inactive brand data for testing."""
    return {
        'name': 'InactiveBrand',
        'description': 'An inactive brand',
        'is_active': False
    }


@pytest_asyncio.fixture
async def inactive_brand(session: AsyncSession, inactive_brand_data: dict) -> Brand:
    """
    Create and persist an inactive test brand in the database.
    """
    db_brand = Brand(
        name=inactive_brand_data["name"],
        description=inactive_brand_data["description"],
        is_active=inactive_brand_data["is_active"]
    )

    session.add(db_brand)
    await session.commit()
    await session.refresh(db_brand)

    return db_brand


@pytest_asyncio.fixture
async def car_data(brand: Brand, user: User) -> dict:
    """Default car data for testing."""
    return {
        'model': 'Corolla',
        'factory_year': 2022,
        'model_year': 2023,
        'color': 'Silver',
        'plate': 'ABC1234',
        'fuel_type': FuelType.FLEX.value,
        'transmission': TransmissionType.AUTOMATIC.value,
        'price': 150000.00,
        'description': 'Well maintained sedan',
        'is_available': True,
        'brand_id': brand.id,
        'owner_id': user.id
    }


@pytest_asyncio.fixture
async def car(session: AsyncSession, car_data: dict, brand: Brand, user: User) -> Car:
    """
    Create and persist a test car in the database.
    """
    db_car = Car(
        model=car_data["model"],
        factory_year=car_data["factory_year"],
        model_year=car_data["model_year"],
        color=car_data["color"],
        plate=car_data["plate"],
        fuel_type=car_data["fuel_type"],
        transmission=car_data["transmission"],
        price=car_data["price"],
        description=car_data["description"],
        is_available=car_data["is_available"],
        brand_id=car_data["brand_id"],
        owner_id=car_data["owner_id"],
    )

    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)

    return db_car


@pytest_asyncio.fixture
async def second_car_data(brand: Brand, user: User) -> dict:
    """Second car data for testing."""
    return {
        'model': 'Camry',
        'factory_year': 2021,
        'model_year': 2022,
        'color': 'Black',
        'plate': 'XYZ5678',
        'fuel_type': FuelType.HYBRID.value,
        'transmission': TransmissionType.CVT.value,
        'price': 180000.00,
        'description': 'Hybrid sedan',
        'is_available': True,
        'brand_id': brand.id,
        'owner_id': user.id
    }


@pytest_asyncio.fixture
async def second_car(session: AsyncSession, second_car_data: dict) -> Car:
    """
    Create and persist a second test car in the database.
    """
    db_car = Car(
        model=second_car_data["model"],
        factory_year=second_car_data["factory_year"],
        model_year=second_car_data["model_year"],
        color=second_car_data["color"],
        plate=second_car_data["plate"],
        fuel_type=second_car_data["fuel_type"],
        transmission=second_car_data["transmission"],
        price=second_car_data["price"],
        description=second_car_data["description"],
        is_available=second_car_data["is_available"],
        brand_id=second_car_data["brand_id"],
        owner_id=second_car_data["owner_id"],
    )

    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)

    return db_car


@pytest_asyncio.fixture
async def auth_headers(client: TestClient, user: User, user_data: dict) -> dict:
    """
    Authenticate and return headers with valid JWT token.
    """
    login_response = client.post('/api/auth/token', json={
        "email": user_data["email"],
        "password": user_data["password"]
    })

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
