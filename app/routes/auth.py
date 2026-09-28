# pyright: reportMissingImports=false

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
)

from app.db import get_db

from app.dependencies import current_user

from app.models.user import User

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserOut,
)

from app.services.auth import (
    authenticate,
    get_user_by_email,
    register_user,
)


router = APIRouter(
    tags=["auth"]
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):

    if get_user_by_email(
        db,
        payload.email,
    ):
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    return register_user(
        db,
        payload.name,
        payload.email,
        payload.password,
    )


@router.post(
    "/login",
    response_model=UserOut,
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    user = authenticate(
        db,
        payload.email,
        payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    response.set_cookie(
        "token",
        create_access_token(user.id),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )

    return user


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        "token"
    )

    return {
        "message": "Logged out"
    }


@router.post("/token")
def token(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):

    if not (user := authenticate(
        db,
        payload.email,
        payload.password,
    )):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "access_token": create_access_token(
            user.id
        ),
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserOut,
)
def me(
    user: User = Depends(current_user),
):

    return user
