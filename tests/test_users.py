from datetime import timedelta

import pytest
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from config import SECRET_KEY, ALGORITHM
from users.auth import get_password_hash, verify_password, create_access_token
from users.models import User

POSTGRESQL_TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/test_cyberpunk"

engine = create_engine(
    POSTGRESQL_TEST_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def create_test_user(db_session):
    """Fixture to create a test user."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    yield user


def test_correct_user_registration(test_client):
    """Example test for user registration."""
    response = test_client.post("/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_register_existing_username(test_client, create_test_user):
    """Test registration with an already existing username."""
    response = test_client.post("/register", json={
        "username": "testuser",
        "email": "newemail@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "This username already registered."


def test_register_existing_email(test_client, create_test_user):
    """Test registration with an already existing email."""
    response = test_client.post("/register", json={
        "username": "anotheruser",
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "This email already registered."


def test_success_user_login(test_client, create_test_user):
    """Test successful user login."""
    response = test_client.post("/token", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(test_client, create_test_user):
    """Test login with incorrect password."""
    response = test_client.post("/token", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password."


def test_login_wrong_username(test_client, create_test_user):
    """Test login with incorrect password."""
    response = test_client.post("/token", data={
        "username": "testuser.",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password."


def test_login_inactive_user(test_client, db_session):
    """Test login with an inactive user."""
    user = User(
        username="inactiveuser",
        email="inactiveuser@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()

    response = test_client.post("/token", data={
        "username": "inactiveuser",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user."


def test_password_hashing():
    plain_password = "password123"
    hashed_password = get_password_hash(plain_password)

    assert hashed_password != plain_password
    assert verify_password(plain_password, hashed_password)


def test_password_verification_failure():
    plain_password = "password123"
    wrong_password = "password123."
    hashed_password = get_password_hash(plain_password)

    assert not verify_password(wrong_password, hashed_password)


def test_jwt_token_creation():
    data = {"sub": "1"}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=30))

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_token["sub"] == "1"


def test_jwt_token_expired():
    expired_token = create_access_token(
        data={"sub": "1"}, expires_delta=timedelta(seconds=-1)
    )

    try:
        jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])
        assert False, "Token should have expired."
    except jwt.ExpiredSignatureError:
        assert True


def test_get_current_user(test_client, create_test_user):
    token = create_access_token(data={"sub": str(create_test_user.id)})

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == create_test_user.username


def test_invalid_token(test_client):
    invalid_token = "invalid.token.value"
    headers = {"Authorization": f"Bearer {invalid_token}"}

    response = test_client.get("/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
