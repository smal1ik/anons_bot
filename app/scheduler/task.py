import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from arq import cron
from arq.connections import RedisSettings, ArqRedis
from decouple import config as env_config

from app.database.requests import get_start_anons, get_all_user, get_end_anons, set_inactive_user, \
    reset_participant_all, get_winners_anons, add_result, get_count_participant

import app.keyboards.keyboard as kb
import app.utils.copy as cp

async def startup(ctx):
    ctx['bot'] = Bot(token=env_config('BOT_TOKEN'))


async def shutdown(ctx):
    await ctx['bot'].session.close()


async def check_anons(ctx):
    inactive_user = set()
    start_anons = await get_start_anons()
    end_anons = await get_end_anons()
    if start_anons:
        tg_ids = await get_all_user()
        for tg_id in tg_ids:
            try:
                await ctx['bot'].send_message(tg_id, text=start_anons.start_msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb.get_check_sub_btn(start_anons.id))
                await asyncio.sleep(0.05)
            except:
                inactive_user.add(tg_id)

    if end_anons:
        tg_ids = await get_all_user(participant=True)
        winners = await get_winners_anons()
        count_participant = await get_count_participant()
        await add_result(end_anons.datetime_end, winners, count_participant)
        await reset_participant_all()
        for tg_id in tg_ids:
            try:
                await ctx['bot'].send_message(tg_id, text=cp.get_end_anons_msg(winners, end_anons.end_msg), parse_mode="HTML", disable_web_page_preview=True)
                await asyncio.sleep(0.03)
            except:
                inactive_user.add(tg_id)

    for tg_id in inactive_user:
        await set_inactive_user(tg_id)

class workersettings:
    max_tries = 3
    redis_settings = RedisSettings(host=env_config('HOST'), port=6379, password=env_config('REDIS_PASSWORD'), database=0, username='default')
    on_startup = startup
    on_shutdown = shutdown
    allow_abort_jobs = True
    cron_jobs = [
        cron(check_anons, minute={0, 10, 20, 30, 40, 50})
    ]