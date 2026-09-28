import importlib

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker

try:
    settings = importlib.import_module("app.core.config").settings
except ModuleNotFoundError as exc:  # pragma: no cover
    if exc.name != "app.core.config":
        raise
    settings = importlib.import_module("core.config").settings


connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = sqlalchemy.create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Common declarative base for all database models."""

    def __repr__(self) -> str:
        """Return a useful representation containing mapped column values."""
        values = ", ".join(
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.__table__.columns
        )
        return f"{type(self).__name__}({values})"


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    import importlib

    importlib.import_module(".models.user", package=__package__)
    importlib.import_module(".models.recommendation", package=__package__)

    Base.metadata.create_all(bind=engine)
