import asyncio

from config import config
from create_bot import scheduler
from db.redis_dao import VacancyRedis
from services.hh import VacancyHh
from src.notifications import send_vacancy_notification


async def __get_new_vacancies():
    resume_ids = {
        "backend": config.hh.backend_resume_id,
        # "devops": config.hh.devops_resume_id
    }
    for resume_title, resume_id in resume_ids.items():
        vacancies = await VacancyHh.get_all(resume_id=resume_id)
        for vacancy in vacancies:
            cache_vacancy = await VacancyRedis.get(key=vacancy.id)
            if cache_vacancy:
                continue
            await send_vacancy_notification(vacancy=vacancy, resume_title=resume_title)
            await VacancyRedis.set(key=vacancy.id, value=resume_id)
            await asyncio.sleep(0.5)


async def create_task():
    scheduler.add_job(
        func=__get_new_vacancies,
        trigger="interval",
        minutes=10,
        misfire_grace_time=None,
    )


if __name__ == "__main__":
    asyncio.run(__get_new_vacancies())
