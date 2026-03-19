import os
import ssl
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "")

Base = declarative_base()
engine = None
SessionLocal = None

if DATABASE_URL:
    # Aiven MySQL requires SSL but we can use ssl_disabled=False approach
    # Strip any existing ssl params and add our own
    clean_url = DATABASE_URL.split("?")[0] if "?" in DATABASE_URL else DATABASE_URL

    connect_args = {}

    if "aivencloud.com" in DATABASE_URL:
        # Aiven: use SSL but skip cert verification for simplicity
        connect_args = {
            "ssl": {"ssl_disabled": False}
        }
    elif "tidbcloud.com" in DATABASE_URL:
        connect_args = {
            "ssl": {"ssl_verify_cert": False}
        }

    engine = create_engine(
        clean_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=2,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if not SessionLocal:
        raise Exception("DATABASE_URL not set")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()