from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# override=True: el .env de este proyecto gana sobre variables globales de Windows
# (evita heredar MERCADOPAGO_* de otro proyecto, p. ej. link de otro negocio).
_backend_dir = Path(__file__).resolve().parent
load_dotenv(_backend_dir / ".env", override=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:1234@localhost/barber"
)

engine = create_engine(DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



