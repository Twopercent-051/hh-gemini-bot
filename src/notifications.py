from config import config
from create_bot import bot
from models import HhVacancyModel
from src.inline import VacanciesInline


async def send_error_notification(code: int, text: str, method: str):
    await bot.send_message(chat_id=config.bot.admin_id, text=f"❗️ERROR {method} {code}\n<code>{text}</code>")


async def send_vacancy_notification(vacancy: HhVacancyModel):
    text = f"💡 <u>{vacancy.title}</u>\n<i>{vacancy.employer}</i>\n\n<i>{vacancy.description}</i>"
    kb = VacanciesInline.vacancy_kb(vacancy=vacancy)
    await bot.send_message(chat_id=config.bot.admin_id, text=text, reply_markup=kb)
