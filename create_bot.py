import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis

from config import config

redis = Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db)
storage = RedisStorage(redis=redis)

bot = Bot(token=config.bot.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)


scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
LOG_LEVEL = logging.INFO
bl.basic_colorized_config(level=LOG_LEVEL)