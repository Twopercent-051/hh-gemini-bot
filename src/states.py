from aiogram.fsm.state import State, StatesGroup


class AuthFSM(StatesGroup):
    code = State()
    tokens = State()
