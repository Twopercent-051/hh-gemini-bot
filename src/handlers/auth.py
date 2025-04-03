from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.redis_dao import AccessTokenRedis, RefreshTokenRedis
from services.hh import AuthHh
from src.states import AuthFSM

router = Router()


@router.message(Command("auth_code"))
async def start_auth_code_handler(message: Message, state: FSMContext):
    text = (
        "Введи код аутентификации. Как получить написано "
        "<a href='https://api.hh.ru/openapi/redoc#section/Avtorizaciya/Avtorizaciya-polzovatelya'>тут</a>"
    )
    await state.set_state(AuthFSM.code)
    await message.answer(text=text)


@router.message(Command("auth_tokens"))
async def start_auth_tokens_handler(message: Message, state: FSMContext):
    text = "Введите <i>access_token</i> и <i>refresh_token</i> через Enter"
    await state.set_state(AuthFSM.tokens)
    await message.answer(text=text)


@router.message(F.text, AuthFSM.code)
async def auth_code_handler(message: Message, state: FSMContext):
    text = "Access-token и refresh-token сохранены в системе"
    auth_data = await AuthHh.with_code(code=message.text)
    if not auth_data:
        return
    await AccessTokenRedis.set(value=auth_data.access_token, expire=auth_data.expires_in)
    await RefreshTokenRedis.set(value=auth_data.refresh_token)
    await state.clear()
    await message.answer(text=text)


@router.message(F.text, AuthFSM.tokens)
async def auth_tokens_handler(message: Message, state: FSMContext):
    text = "Access-token и refresh-token сохранены в системе"
    try:
        access_token = message.text.split("\n")[0]
        refresh_token = message.text.split("\n")[1]
    except IndexError:
        text = "Нужно ввести два ключа через Enter"
        await message.answer(text=text)
        return
    await AccessTokenRedis.set(value=access_token, expire=1209599)
    await RefreshTokenRedis.set(value=refresh_token)
    await state.clear()
    await message.answer(text=text)
