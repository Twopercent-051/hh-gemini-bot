from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.redis_dao import RespondsRedis, VacancyRedis
from services.gemini import generate_respond
from services.hh import ResumeHh, VacancyHh
from src.inline import VacanciesInline
from src.notifications import send_error_notification

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    text = "Состояния сброшены"
    await state.clear()
    await message.answer(text=text)


@router.callback_query(F.data.split(":")[0] == "respond")
async def create_respond_handler(callback: CallbackQuery):
    vacancy_id = callback.data.split(":")[1]
    resume_id = await VacancyRedis.get(key=vacancy_id)
    if not resume_id:
        return
    resume = await ResumeHh.get_one_or_none(resume_id=resume_id)
    vacancy = await VacancyHh.get_one_or_none(vacancy_id=vacancy_id)
    if not resume or not vacancy:
        return
    prompt = (
        f"Моё резюме: {resume.title}, описание: {resume.description}, мои навыки: {resume.skills}. "
        f"Напиши короткий (до 2000 символов) отклик на вакансию {vacancy.title} с требованиями "
        f"{vacancy.description}. Никогда не добавляй в текст что-то, что "
        f"требует ручной вставки (например С уважением,[Ваше Имя]). Придерживайся инфо-стиля"
    )
    respond = await generate_respond(prompt=prompt)
    ps_text = (
        "\nPS Если вам показалось, что этот отклик написан нейросетью, то так и есть. Я действительно сделал "
        "Телеграм-бот для генерации и отправки откликов на вакансии с помощью Gemini "
        "https://github.com/Twopercent-051/hh-gemini-bot\nВсё оттого, что я не SMM-менеджер и не умею писать "
        'под каждую вакансию "продающий" отклик. Зато умею и люблю писать работающие приложения и максимально '
        "автоматизировать работу."
    )
    respond += ps_text
    await callback.message.delete()
    kb = VacanciesInline.respond_kb(vacancy_id=vacancy_id)
    await RespondsRedis.set(key=vacancy_id, value=respond)
    await callback.message.answer(text=f"<code>{respond}</code>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.split(":")[0] == "send_respond")
async def send_respond_clb_handler(callback: CallbackQuery, state: FSMContext):
    vacancy_id = callback.data.split(":")[1]
    resume_id = await VacancyRedis.get(key=vacancy_id)
    respond = await RespondsRedis.get(key=vacancy_id)
    if not respond:
        await send_error_notification(code=0, text="Respond not found", method="send_respond_clb_handler")
        return
    await VacancyHh.respond(resume_id=resume_id, vacancy_id=vacancy_id, message=respond)
    await callback.message.delete()
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "skip")
async def skip_respond_clb_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
