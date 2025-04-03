
import redis.asyncio as redis

from config import config





class __BaseRedis:
    prefix = ""
    redis_url = f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db}"
    pool = redis.ConnectionPool.from_url(url=redis_url)
    redis_instance = redis.Redis(connection_pool=pool)
    expire = None

    @classmethod
    async def get(cls, key: str = "") -> str | None:
        response = await cls.redis_instance.get(name=f"{cls.prefix}_{key}")
        if not response:
            return
        return response.decode("utf-8")

    @classmethod
    async def set(cls, value: str, key: str="",  expire: int | None = None):
        await cls.redis_instance.set(
            name=f"{cls.prefix}_{key}",
            value=value,
            ex=expire or cls.expire
        )

class AccessTokenRedis(__BaseRedis):
    prefix = "accesses_token"

class RefreshTokenRedis(__BaseRedis):
    prefix = "refresh_token"

class VacancyRedis(__BaseRedis):
    prefix = "vacancies"
    expire = 3600*24*3

class RespondsRedis(__BaseRedis):
    prefix = "responds"
    expire = 3600*24*3