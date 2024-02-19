import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from Utils import chunks

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_async_engine(f"postgresql+asyncpg://"
                             f"{os.getenv('DB_USER')}"
                             f":{os.getenv('DB_PASS')}"
                             f"@{os.getenv('DB_HOST')}"
                             f":{os.getenv('DB_PORT')}"
                             f"/{os.getenv('DB_BASE')}")

Base = declarative_base()


class Record(Base):
    __tablename__ = 'parsing_data'

    id = Column(Integer, primary_key=True)
    ID = Column(String(10), nullable=False)
    Data_length = Column(String(10), nullable=False)
    Length = Column(String(100), nullable=False)
    Name = Column(String(200), nullable=False)
    RusName = Column(String(200), nullable=False)
    Scaling = Column(String(50), nullable=False)
    Range = Column(String(50), nullable=False)
    SPN = Column(String(100), nullable=False)


async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def insert_data(data_part: list):
    data_list = [Record(
        ID=record['ID'],
        Data_length=record['Data_length'],
        Length=record['Length'],
        Name=record['Name'],
        RusName=record['RusName'],
        Scaling=record['Scaling'],
        Range=record['Range'],
        SPN=record['SPN']
    ) for record in data_part]
    async with async_session_maker() as orm_session:
        orm_session.add_all(data_list)
        await orm_session.commit()


async def load_data(data: list):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    chunk_size = 10
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
        n = 1
        for data_part in chunks(data, chunk_size):
            if not data_part:
                break
            in_data = insert_data(data_part)
            task = asyncio.create_task(in_data)
            await task
            n += chunk_size

    print("Данные загружены в базу.")
