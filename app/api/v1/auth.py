from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginInput, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

RESPONSES = {
    400: {"description": "Bad Request"},
    500: {"description": "Internal Server Error"},
}


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


@router.post("/login", response_model=Token, responses=RESPONSES)
def login(credentials: LoginInput, db: Session = Depends(get_db)):
    logger.info("Login attempt for email={email}", email=credentials.email)
    user = get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning("Login failed for email={email}", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(subject=user.id)
    logger.info("Login successful for user_id={user_id}", user_id=user.id)
    return Token(access_token=access_token)
