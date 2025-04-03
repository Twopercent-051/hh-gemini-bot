from typing import Union

from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import config
from src.handlers.general import router as general_router
from src.handlers.auth import router as auth_router


class AdminFilter(BaseFilter):

    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        if isinstance(obj, Message):
            return str(obj.chat.id) == str(config.bot.admin_id)
        else:
            return str(obj.message.chat.id) == str(config.bot.admin_id)


router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

router.include_routers(general_router, auth_router)
