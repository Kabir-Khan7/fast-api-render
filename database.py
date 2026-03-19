import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

# TiDB Cloud requires SSL — detect if we're in production
connect_args = {}
if DATABASE_URL and "tidbcloud" in DATABASE_URL:
    connect_args = {
        "ssl": {
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }
    }

engine = SessionLocal = None
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    if not SessionLocal:
        raise Exception("DATABASE_URL not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()