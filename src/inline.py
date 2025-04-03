from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models import HhVacancyModel


class VacanciesInline:

    @staticmethod
    def vacancy_kb(vacancy: HhVacancyModel):
        kb = [
            [InlineKeyboardButton(text="👀 Посмотреть", url=vacancy.url)],
            [InlineKeyboardButton(text="Сформировать отклик", callback_data=f"respond:{vacancy.id}")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)

    @staticmethod
    def respond_kb(vacancy_id: int):
        kb = [[InlineKeyboardButton(text="Отправить как есть", callback_data=f"send_respond:{vacancy_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=kb)
