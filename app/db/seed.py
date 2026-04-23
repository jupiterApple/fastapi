from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.core.security import get_password_hash
from app.models.user import User


def seed_initial_user(db: Session) -> None:
    email = settings.FIRST_SUPERUSER_EMAIL
    if not email or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info("Seed skipped: FIRST_SUPERUSER_EMAIL/PASSWORD not configured")
        return

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.info("Seed skipped: user already exists email={email}", email=email)
        return

    user = User(
        email=email,
        full_name=settings.FIRST_SUPERUSER_NAME,
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        is_active=1,
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Seed failed: error inserting initial user")
        return
    db.refresh(user)
    logger.info("Seed: initial user created user_id={user_id} email={email}", user_id=user.id, email=email)
