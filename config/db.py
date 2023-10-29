from sqlalchemy import create_engine,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.automap import automap_base

import os

load_dotenv('.env')
username = os.getenv('database_username')
password = os.getenv('database_password')
database_hostname = os.getenv('database_hostname')
db_name = os.getenv('database_name')


engine = create_engine(f"mysql+pymysql://{username}:{password}@{database_hostname}/{db_name}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
ExistBase = automap_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# engine = create_engine("mysql+pymysql://root@localhost:3306/fastapi")

meta = MetaData()
conn = engine.connect() 

