from fastapi import (  # pyright: ignore[reportMissingImports]
    APIRouter,
    Depends,
)

from sqlalchemy import select  # pyright: ignore[reportMissingImports]

from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.db import get_db  # pyright: ignore[reportMissingImports]

from app.dependencies import (  # pyright: ignore[reportMissingImports]
    current_user,
)

import app.models.recommendation  # pyright: ignore[reportMissingImports]
import app.models.user  # pyright: ignore[reportMissingImports]


router = APIRouter(
    tags=["session"]
)


@router.get(
    "/session-info"
)
def session_info(
    user: app.models.user.User = Depends(
        current_user
    ),
):

    return {
        "logged_in": True,
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
    }


@router.get(
    "/session-data"
)
def session_data(
    user: app.models.user.User = Depends(
        current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    rows = db.scalars(
        select(app.models.recommendation.Recommendation)
        .where(
            app.models.recommendation.Recommendation.user_id
            == user.id
        )
    ).all()

    return {
        "user_id": user.id,
        "email": user.email,
        "recommendation_count": len(
            rows
        ),
    }


@router.get(
    "/history"
)
def history(
    user: app.models.user.User = Depends(
        current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    rows = db.scalars(
        select(app.models.recommendation.Recommendation)
        .where(
            app.models.recommendation.Recommendation.user_id
            == user.id
        )
        .order_by(
            app.models.recommendation.Recommendation.created_at.desc()
        )
    ).all()

    return [
        {
            "id": row.id,
            "planner": row.planner,
            "title": row.title,
            "request": row.request_data,
            "result": row.result_data,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
