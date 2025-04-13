import datetime

from app.database.models import User, async_session, Anons, Result
from sqlalchemy import select, BigInteger, update, delete, func, case


async def add_user(tg_id: BigInteger, first_name: str, username: str, full_name: str):
    """
    Функция добавляет пользователя в БД
    """
    async with async_session() as session:
        if not first_name:
            first_name = 'None'
        if not username:
            username = ''
        if not full_name:
            full_name = str(tg_id)
        session.add(User(
            tg_id=tg_id,
            first_name=first_name,
            username=username,
            full_name=full_name))
        await session.commit()


async def get_user(tg_id: BigInteger):
    """
    Получаем пользователя по tg_id
    """
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))
        return result


async def get_all_user():
    """
    Получаем всех пользователей
    """
    async with async_session() as session:
        result = await session.scalars(select(User.tg_id).where(User.is_active == True))
        return result.fetchall()


async def set_inactive_user(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(is_active=False))
        await session.commit()


async def set_participant_user(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(participant=True))
        await session.commit()

async def get_count_participant():
    async with async_session() as session:
        result = (await session.execute(func.count(User.id))).scalar()
        return result

async def add_result(datetime_end, winners, participants):
    winners_check = []
    for winner in winners:
        if winner.username:
            winners_check.append(winner.username)
        else:
            winners_check.append(f"{winner.full_name} {winner.tg_id}")
    async with async_session() as session:
        session.add(Result(
            datetime_end=datetime_end,
            winner_1=winners_check[0],
            winner_2=winners_check[1],
            winner_3=winners_check[2],
            participants=participants))
        await session.commit()

async def get_winners_anons():
    async with async_session() as session:
        result = await session.scalars(select(User).where(User.participant == True).order_by(func.random()).limit(3))
        return result.fetchall()


async def reset_participant_all():
    async with async_session() as session:
        await session.execute(update(User).values(participant=False))
        await session.commit()


async def get_actual_anons(for_user=False):
    today = datetime.datetime.now()
    async with async_session() as session:
        if not for_user:
            result = await session.scalars(select(Anons).where(Anons.datetime_end > today).order_by(Anons.datetime_start))
        else:
            result = await session.scalars(
                select(Anons).where(Anons.datetime_end > today, Anons.datetime_start < today).order_by(Anons.datetime_start)
            )
    return result.fetchall()


async def get_anons(anons_id):
    async with async_session() as session:
        result = await session.scalar(select(Anons).where(Anons.id == int(anons_id)))
    return result


async def new_anons(datetime_start, datetime_end, start_msg, end_msg):
    async with async_session() as session:
        session.add(Anons(
            datetime_start=datetime_start,
            datetime_end=datetime_end,
            start_msg=start_msg,
            end_msg=end_msg))
        await session.commit()


async def edit_anons(anons_id, type_edit, time_edit, new_data):
    async with async_session() as session:
        if type_edit == 'msg':
            if time_edit == 'start':
                await session.execute(update(Anons).where(Anons.id == int(anons_id)).values(start_msg=new_data))
            else:
                await session.execute(update(Anons).where(Anons.id == int(anons_id)).values(end_msg=new_data))
        else:
            new_data = datetime.datetime.strptime(new_data, "%d.%m.%y %H:%M")
            if time_edit == 'start':
                await session.execute(update(Anons).where(Anons.id == int(anons_id)).values(datetime_start=new_data))
            else:
                await session.execute(update(Anons).where(Anons.id == int(anons_id)).values(datetime_end=new_data))
        await session.commit()


async def remove_anons(anons_id):
    async with async_session() as session:
        await session.execute(delete(Anons).where(Anons.id == int(anons_id)))
        await session.commit()


async def get_start_anons():
    now = datetime.datetime.now()
    time_threshold = now - datetime.timedelta(minutes=15)
    async with async_session() as session:
        result = await session.scalar(
            select(Anons).where(Anons.datetime_start <= now, Anons.datetime_start >= time_threshold))
    return result


async def get_end_anons():
    now = datetime.datetime.now()
    time_threshold = now - datetime.timedelta(minutes=15)
    async with async_session() as session:
        result = await session.scalar(
            select(Anons).where(Anons.datetime_end <= now, Anons.datetime_end >= time_threshold))
    return result
