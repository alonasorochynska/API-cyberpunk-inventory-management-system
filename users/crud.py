from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from users.models import User
from users.schemas import UserCreate
from users.auth import get_password_hash, verify_password, create_access_token


def create_user(db: Session, user: UserCreate):
    db_user_by_username = check_user_existence_by_username_or_email(db=db, field_name="username", value=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="This username already registered.")

    db_user_by_email = check_user_existence_by_username_or_email(db=db, field_name="email", value=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="This email already registered.")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """
    Функция для аутентификации пользователя по имени и паролю
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password.")

    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")

    return create_access_token(data={"sub": str(user.id)})


def check_user_existence_by_username_or_email(db: Session, field_name: str, value: str):
    """
    Универсальная функция для поиска пользователя по любому полю
    """
    if field_name == "username":
        return db.query(User).filter(User.username == value).first()
    elif field_name == "email":
        return db.query(User).filter(User.email == value).first()
    return None


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
