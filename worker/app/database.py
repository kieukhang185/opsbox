import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opsbox.db")
QUEUE_NAME = os.getenv("QUEUE_NAME", "default")

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
