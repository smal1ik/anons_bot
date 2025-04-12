from app.handlers.handler import router_main

import asyncio
import logging
import sys

from decouple import config

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

async def main():
    bot = Bot(token=config('BOT_TOKEN'))
    redis_pool = await create_pool(
        RedisSettings(host=config('HOST'), port=6379, password=config('REDIS_PASSWORD'), database=1, username='default'))
    await bot.delete_webhook()
    dp = Dispatcher(storage=RedisStorage.from_url(config('REDIS_URL')))
    dp.include_router(router_main)
    await dp.start_polling(bot, polling_timeout=100, arqredis=redis_pool)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
        print("Bot start")
    except KeyboardInterrupt:
        print('Bot stop')
    except Exception as e:
        print(e)
