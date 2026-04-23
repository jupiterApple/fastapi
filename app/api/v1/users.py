from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

RESPONSES = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    500: {"description": "Internal Server Error"},
}


@router.get("/me", response_model=UserRead, responses=RESPONSES)
def read_current_user(current_user: User = Depends(get_current_user)):
    logger.info("Read current user user_id={user_id}", user_id=current_user.id)
    return current_user


@router.get("/", response_model=list[UserRead], responses=RESPONSES)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "List users requested by user_id={user_id} skip={skip} limit={limit}",
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserRead, responses=RESPONSES)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Get user requested by user_id={requester} target_id={target}",
        requester=current_user.id,
        target=user_id,
    )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses=RESPONSES,
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Create user request by user_id={user_id} for email={email}",
        user_id=current_user.id,
        email=user_in.email,
    )
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        logger.warning("User creation failed: email already registered {email}", email=user_in.email)
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error saving new user to database")
        raise HTTPException(status_code=500, detail="Unable to create user")
    db.refresh(user)
    logger.info("User created successfully user_id={user_id}", user_id=user.id)
    return user


@router.put("/{user_id}", response_model=UserRead, responses=RESPONSES)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Update user requested by user_id={requester} target_id={target}",
        requester=current_user.id,
        target=user_id,
    )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = user_in.model_dump(exclude_unset=True)

    if "email" in data and data["email"] != user.email:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = data["email"]

    if "full_name" in data:
        user.full_name = data["full_name"]

    if data.get("password"):
        user.hashed_password = get_password_hash(data["password"])

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error updating user user_id={user_id}", user_id=user_id)
        raise HTTPException(status_code=500, detail="Unable to update user")
    db.refresh(user)
    logger.info("User updated user_id={user_id}", user_id=user.id)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Delete user requested by user_id={requester} target_id={target}",
        requester=current_user.id,
        target=user_id,
    )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error deleting user user_id={user_id}", user_id=user_id)
        raise HTTPException(status_code=500, detail="Unable to delete user")
    logger.info("User deleted user_id={user_id}", user_id=user_id)
    return None
