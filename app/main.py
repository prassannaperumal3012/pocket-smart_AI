from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path

from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import (  # pyright: ignore
    CORSMiddleware,
)
from fastapi.routing import APIRouter  # pyright: ignore[reportMissingImports]
from fastapi.staticfiles import (  # pyright: ignore
    StaticFiles,
)
from starlette.middleware.sessions import (  # pyright: ignore
    SessionMiddleware,
)

from app.core.config import settings  # pyright: ignore[reportMissingImports]

from app.db import init_db

from app.routes.auth import (  # pyright: ignore[reportMissingImports]
    router as auth_router,
)

try:
    planner_router = import_module("app.routes.planners").router
except (ImportError, AttributeError):
    planner_router = APIRouter()
try:
    session_router = import_module("app.routes.session").router
except (ImportError, AttributeError):
    session_router = APIRouter()

try:
    pages_router = import_module("app.routes.pages").router
except (ImportError, AttributeError):
    pages_router = APIRouter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="PocketSmart AI",
    description="Budget-aware AI recommendation assistant.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
)

static_dir = Path(__file__).parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=static_dir),
    name="static",
)

app.include_router(pages_router)
app.include_router(auth_router, prefix="/api")
app.include_router(planner_router, prefix="/api")
app.include_router(session_router, prefix="/api")


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "pocketsmart-ai",
    }
