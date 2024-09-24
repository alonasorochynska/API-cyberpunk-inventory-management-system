from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from users import auth, crud, models, schemas


router = APIRouter()


@router.post("/register", response_model=schemas.UserRead, tags=["user"])
def register_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> schemas.UserRead:
    """Register a new user."""
    user = crud.create_user(db=db, user=user)
    return schemas.UserRead.model_validate(user)


@router.post("/token", tags=["user"])
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> dict:
    """Log in and generate an access token."""
    access_token = crud.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserRead, tags=["user"])
def read_users_me(
        current_user: models.User = Depends(auth.get_current_user)
) -> schemas.UserRead:
    """Get the current authenticated user's information."""
    return schemas.UserRead.model_validate(current_user)
