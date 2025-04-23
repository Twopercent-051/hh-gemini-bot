from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.redis_dao import RespondsRedis
from services.gemini import generate_respond
from services.hh import ResumeHh, VacancyHh
from src.inline import VacanciesInline
from src.notifications import send_error_notification
from src.states import RespondFSM

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    text = "Состояния сброшены"
    await state.clear()
    await message.answer(text=text)


@router.callback_query(F.data.split(":")[0] == "respond")
async def create_respond_handler(callback: CallbackQuery, state: FSMContext):
    vacancy_id = callback.data.split(":")[1]
    resume = await ResumeHh.get_one_or_none()
    vacancy = await VacancyHh.get_one_or_none(vacancy_id=vacancy_id)
    if not resume or not vacancy:
        return
    prompt = (
        f"Моё резюме: {resume.title}, описание: {resume.description}, мои навыки: {resume.skills}. "
        f"Напиши короткий (до 3000 символов) отклик на вакансию {vacancy.title} с требованиями "
        f"{vacancy.description}. Если в вакансии требуется показать свой Github или Gitlab, то пришли вот этот "
        f"аккаунт https://github.com/twopercent051?tab=repositories. Уточни, что там находятся тестовые задание "
        f"(некоммерческие). Никогда не добавляй в текст что-то, что "
        f"требует ручной вставки (например С уважением,[Ваше Имя]). Придерживайся инфо-стиля"
    )
    respond = await generate_respond(prompt=prompt)
    respond += (
        "\n\nВы можете связаться со мной в Телеграм @two_percent или по электронной почте twopercent051@yandex.ru"
    )
    await callback.message.delete()
    kb = VacanciesInline.respond_kb(vacancy_id=vacancy_id)
    await RespondsRedis.set(key=vacancy_id, value=respond)
    await state.set_state(RespondFSM.text)
    await state.update_data(vacancy_id=vacancy_id)
    await callback.message.answer(text=f"<code>{respond}</code>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.split(":")[0] == "send_respond")
async def send_respond_clb_handler(callback: CallbackQuery, state: FSMContext):
    vacancy_id = callback.data.split(":")[1]
    respond = await RespondsRedis.get(key=vacancy_id)
    if not respond:
        await send_error_notification(code=0, text="Respond not found", method="send_respond_clb_handler")
        return
    await VacancyHh.respond(vacancy_id=vacancy_id, message=respond)
    await callback.message.delete()
    await state.clear()
    await callback.answer()


@router.message(F.text, RespondFSM.text)
async def send_respond_msg_handler(message: Message, state: FSMContext):
    respond = message.text
    vacancy_id = await state.get_data()
    await VacancyHh.respond(vacancy_id=vacancy_id, message=respond)
    await state.clear()


@router.callback_query(F.data == "skip")
async def skip_respond_clb_handler(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
