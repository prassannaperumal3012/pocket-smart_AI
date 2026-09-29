from pathlib import Path
from importlib import import_module

# cspell:ignore homeplanner partyplanner jewelryplanner

from app.db import SessionLocal

User = import_module("app.models.user").User

try:
    from fastapi import (  # type: ignore[reportMissingImports]
        APIRouter,
        Request,
    )
except ModuleNotFoundError:  # pragma: no cover
    class APIRouter:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    class Request:  # type: ignore[no-redef]
        pass

try:
    from fastapi.responses import (  # type: ignore[reportMissingImports]
        HTMLResponse,
    )
except ModuleNotFoundError:  # pragma: no cover
    from starlette.responses import (  # type: ignore[no-redef]
        HTMLResponse,
    )

try:
    from fastapi.templating import (  # type: ignore[reportMissingImports]
        Jinja2Templates,
    )
except ModuleNotFoundError:  # pragma: no cover
    from starlette.templating import Jinja2Templates  # type: ignore[no-redef]

decode_access_token = import_module(
    "app.core.security"
).decode_access_token


router = APIRouter()

PLANNER_TEMPLATES = {
    "home": "homeplanner.html",
    "party": "partyplanner.html",
    "jewelry": "jewelryplanner.html",
}


templates = Jinja2Templates(
    directory=str(
        Path(__file__)
        .resolve()
        .parents[1]
        / "templates"
    )
)


def _user_from_cookie(
    request: Request,
):

    token = request.cookies.get(
        "token"
    )

    if not token:
        return None

    user_id = decode_access_token(
        token
    )

    if not user_id:
        return None

    with SessionLocal() as db:
        return db.get(
            User,
            user_id,
        )


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": _user_from_cookie(
                request
            ),
        },
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "user": _user_from_cookie(
                request
            ),
        },
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "user": _user_from_cookie(
                request
            ),
        },
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": _user_from_cookie(
                request
            ),
        },
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse,
)
def planner_page(
    request: Request,
    planner: str,
):

    template_name = PLANNER_TEMPLATES.get(planner)

    if template_name is None:

        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={},
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "user": _user_from_cookie(
                request
            ),
        },
    )
