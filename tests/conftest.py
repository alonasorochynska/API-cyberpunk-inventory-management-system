from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import pytest

from database import Base, get_db
from inventory import schemas, crud, models
from main import app
from users.auth import get_password_hash
from users.models import User


POSTGRESQL_TEST_DATABASE_URL = (
    "postgresql://test_user:test_password@localhost:5432/test_cyberpunk"
)

engine = create_engine(
    POSTGRESQL_TEST_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Create a new database session with a rollback at the end of the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    """
    Create a test client that uses the overridden
    get_db fixture to return a session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def create_test_user(db_session: Session) -> User:
    """Fixture to create a test user."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash(password="password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    yield user


@pytest.fixture(scope="function")
def create_test_category(db_session: Session) -> models.Category:
    """Fixture to create a test category."""
    category_data = schemas.CategoryCreate(name="Weapon")
    category = crud.create_category(db=db_session, category=category_data)
    db_session.add(category)
    db_session.commit()
    yield category


@pytest.fixture(scope="function")
def create_test_item(
    db_session: Session,
        create_test_user: User,
        create_test_category: models.Category
) -> models.Item:
    """Fixture to create a test item."""
    item = models.Item(
        name="Test Item",
        description="Test Description",
        category=create_test_category.name,
        quantity=5,
        price=100.0,
        creator_id=create_test_user.id
    )
    db_session.add(item)
    db_session.commit()
    yield item
