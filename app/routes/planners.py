# pyright: reportMissingImports=false
from io import BytesIO
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from PIL import Image

from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import current_user

import importlib

from app.models.user import User
from app.schemas.planners import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
)

generate_recommendation = importlib.import_module(
    "app.services.recommender"
).generate_recommendation

Recommendation = importlib.import_module(
    "app.models.recommendation"
).Recommendation


router = APIRouter(
    tags=["planners"]
)


def save_history(
    db: Session,
    user: User,
    planner: str,
    request_data: dict,
    result,
):

    row = Recommendation(
        user_id=user.id,
        planner=planner,
        title=result.summary[:250],
        request_data=request_data,
        result_data=result.model_dump(),
    )

    db.add(row)

    db.commit()


@router.post(
    "/generate-home"
)
def generate_home(
    payload: HomeRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):

    result = generate_recommendation(
        "home",
        payload,
    )

    save_history(
        db,
        user,
        "home",
        payload.model_dump(),
        result,
    )

    return result


@router.post(
    "/generate-party"
)
def generate_party(
    payload: PartyRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):

    result = generate_recommendation(
        "party",
        payload,
    )

    save_history(
        db,
        user,
        "party",
        payload.model_dump(),
        result,
    )

    return result


@router.post(
    "/generate-jewelry"
)
async def generate_jewelry(
    budget: Annotated[
        float,
        Form(gt=0),
    ],

    occasion: Annotated[
        str,
        Form(min_length=2),
    ],

    style: Annotated[
        str,
        Form(),
    ] = "elegant",

    metal: Annotated[
        str,
        Form(),
    ] = "",

    outfit_description: Annotated[
        str,
        Form(),
    ] = "",

    city: Annotated[
        str,
        Form(),
    ] = "",

    image: UploadFile | None = File(
        default=None
    ),

    user: User = Depends(
        current_user
    ),

    db: Session = Depends(
        get_db
    ),
):  # sourcery skip: raise-from-previous-error

    image_obj = None

    if image:

        raw = await image.read()

        if len(raw) > 5 * 1024 * 1024:

            raise HTTPException(
                status_code=413,
                detail="Image is too large. Maximum size is 5 MB.",
            )

        try:

            image_obj = Image.open(
                BytesIO(raw)
            ).convert("RGB")

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid image.",
            )

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        metal=metal,
        outfit_description=outfit_description,
        city=city,
    )

    result = generate_recommendation(
        "jewelry",
        payload,
        image_obj,
    )

    save_history(
        db,
        user,
        "jewelry",
        payload.model_dump(),
        result,
    )

    return result
