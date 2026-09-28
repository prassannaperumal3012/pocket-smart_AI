from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import (
    hash_password,
    verify_password,
)
from ..models.user import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.email == email.lower().strip()
        )
    )


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:

    user = User(
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    if not (user := get_user_by_email(db, email)):
        return None

    return user if verify_password(password, user.password_hash) else None
