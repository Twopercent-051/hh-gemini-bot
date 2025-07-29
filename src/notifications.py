from config import config
from create_bot import bot
from models import HhVacancyModel
from src.inline import VacanciesInline


async def send_error_notification(code: int, text: str, method: str):
    await bot.send_message(chat_id=config.bot.admin_id, text=f"❗️ERROR {method} {code}\n<code>{text}</code>")


async def send_vacancy_notification(resume_title: str, vacancy: HhVacancyModel):
    test_text = "❗️ ЕСТЬ ТЕСТОВОЕ\n\n" if vacancy.has_test else ""
    text = (
        f"{test_text}💡 <u>{vacancy.title}</u>\n<i>{vacancy.employer} "
        f"({vacancy.area})</i>\n{vacancy.work_format}\n\n<i>{vacancy.description}</i>\n\n{resume_title.lower()}"
    )
    kb = VacanciesInline.vacancy_kb(vacancy=vacancy)
    try:
        await bot.send_message(chat_id=config.bot.admin_id, text=text, reply_markup=kb)
    except Exception as e:
        await send_error_notification(code=e, text=str(e), method="send_vacancy_notification")
