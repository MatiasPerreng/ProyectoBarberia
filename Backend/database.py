from sqlalchemy import create_engine    
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:1234@localhost/barber"

engine = create_engine(DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

base = declarative_base()