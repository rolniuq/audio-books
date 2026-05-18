from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Determine if we're using SQLite (which needs check_same_thread=False)
# or another database like PostgreSQL
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite"):
    # SQLite-specific arguments
    engine = create_engine(
        database_url, 
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL and other databases
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import book
    Base.metadata.create_all(bind=engine)