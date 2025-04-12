from sqlalchemy import BigInteger, Boolean, DateTime, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from decouple import config

engine = create_async_engine(config('POSTGRESQL'), echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    full_name: Mapped[str] = mapped_column()
    participant = mapped_column(Boolean, default=False)
    is_active = mapped_column(Boolean, default=True)


class Result(Base):
    __tablename__ = 'results'
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime_end = mapped_column(DateTime)
    winner_1: Mapped[str] = mapped_column()
    winner_2: Mapped[str] = mapped_column()
    winner_3: Mapped[str] = mapped_column()
    participants = mapped_column(Integer)


class Anons(Base):
    __tablename__ = 'anons'
    id: Mapped[int] = mapped_column(primary_key=True)
    datetime_start = mapped_column(DateTime)
    datetime_end = mapped_column(DateTime)
    start_msg: Mapped[str] = mapped_column()
    end_msg: Mapped[str] = mapped_column()
    is_finished = mapped_column(Boolean, default=False)
