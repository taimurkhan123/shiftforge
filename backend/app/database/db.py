from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

# SQLite needs check_same_thread=False when used with FastAPI's threadpool
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables. Called at app startup."""
    # Import models so SQLModel registers them before create_all
    from app.database import tables  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)