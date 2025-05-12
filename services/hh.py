import asyncio
from functools import wraps

import httpx

from config import config
from create_bot import logger
from db.redis_dao import AccessTokenRedis, RefreshTokenRedis
from models import HhAuthModel, HhResumeModel, HhVacancyModel
from src.notifications import send_error_notification


def with_headers(with_bearer: bool = True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "HH-User-Agent": f"{config.hh.app_title}/1.0",
            }
            if with_bearer:
                access_token = await AccessTokenRedis.get()
                if not access_token:
                    auth_data = await AuthHh.with_refresh_token()
                    await AccessTokenRedis.set(value=auth_data.access_token, expire=auth_data.expires_in)
                    await RefreshTokenRedis.set(value=auth_data.refresh_token)
                headers["Authorization"] = f"Bearer {access_token}"
            kwargs["headers"] = headers
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class __BaseHh:

    client_id = config.hh.client_id
    client_secret = config.hh.client_secret

    @staticmethod
    async def _drop_access_token(response: httpx.Response, method: str):
        if response.status_code in [401, 403]:
            auth_data = await AuthHh.with_refresh_token()
            await AccessTokenRedis.set(value=auth_data.access_token, expire=auth_data.expires_in)
            await RefreshTokenRedis.set(value=auth_data.refresh_token)
        await send_error_notification(text=response.text, code=response.status_code, method=method)


class AuthHh(__BaseHh):

    url = "https://api.hh.ru/token"

    @classmethod
    @with_headers(with_bearer=False)
    async def __auth_request(cls, data: dict, headers: dict[str, str]) -> HhAuthModel | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=cls.url, data=data, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return HhAuthModel(**response_data)
            await cls._drop_access_token(response=response, method="auth")
            return None

    @classmethod
    async def with_code(cls, code: str) -> HhAuthModel | None:
        data = {
            "grant_type": "authorization_code",
            "client_id": cls.client_id,
            "client_secret": cls.client_secret,
            "code": code,
        }
        return await cls.__auth_request(data=data)

    @classmethod
    async def with_refresh_token(cls) -> HhAuthModel | None:
        refresh_token = await RefreshTokenRedis.get()
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        return await cls.__auth_request(data=data)


class ResumeHh(__BaseHh):

    @classmethod
    @with_headers()
    async def get_one_or_none(cls, resume_id: str, headers: dict[str, str]) -> HhResumeModel | None:
        url = f"https://api.hh.ru/resumes/{resume_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                logger.info(response_data)
                return HhResumeModel(
                    id=resume_id,
                    title=response_data["title"],
                    description=response_data["skills"],
                    skills=response_data["skill_set"],
                )
            await cls._drop_access_token(response=response, method="resume")
            return None


class VacancyHh(__BaseHh):

    @classmethod
    @with_headers()
    async def get_all(cls, resume_id: str, headers: dict[str, str]) -> list[HhVacancyModel]:
        url = f"https://api.hh.ru/resumes/{resume_id}/similar_vacancies"
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params={"per_page": 100, "period": 2})
            if response.status_code == 200:
                response_data = response.json()
                result = []
                for item in response_data["items"]:
                    description = [item["snippet"]["responsibility"], item["snippet"]["requirement"]]
                    filtered_description = filter(None, description)
                    work_formats = [i["name"] for i in item["work_format"]] if item["work_format"] else []
                    vacancy = HhVacancyModel(
                        id=item["id"],
                        title=item["name"],
                        description="\n".join(filtered_description),
                        url=item["alternate_url"],
                        employer=item["employer"]["name"],
                        area=item["area"]["name"],
                        work_format=", ".join(work_formats),
                        has_test=item["has_test"],
                    )
                    result.append(vacancy)
                return result
            else:
                await cls._drop_access_token(response=response, method="vacancies")
                return []

    @classmethod
    @with_headers()
    async def get_one_or_none(cls, vacancy_id: int, headers: dict[str, str]) -> HhVacancyModel | None:
        url = f"https://api.hh.ru/vacancies/{vacancy_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return HhVacancyModel(
                    id=vacancy_id,
                    title=response_data["name"],
                    description=response_data["description"],
                    url=response_data["alternate_url"],
                    employer="",
                    area="",
                    work_format="",
                    has_test=False,
                )
            await cls._drop_access_token(response=response, method="vacancy")
            return None

    @classmethod
    @with_headers()
    async def respond(cls, resume_id: str, vacancy_id: int, message: str, headers: dict[str, str]):
        url = "https://api.hh.ru/negotiations"
        data = {"message": message, "vacancy_id": vacancy_id, "resume_id": resume_id}
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data, headers=headers)
            if response.status_code != 201:
                logger.error(response.text)
            if response.status_code in [401, 403]:
                await cls._drop_access_token(response=response, method="respond")


if __name__ == "__main__":
    asyncio.run(VacancyHh.get_all())
