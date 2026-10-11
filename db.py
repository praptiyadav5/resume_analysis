import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(Path(__file__).with_name(".ENV"))
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"ssl": {"ssl": True}},
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()