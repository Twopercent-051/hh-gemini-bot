import asyncio


from create_bot import bot, dp, logger, scheduler

from src.routers import router
from utils.scheduler_util import create_task


async def main():
    logger.info("Starting bot")
    dp.include_router(router=router)
    scheduler.remove_all_jobs()
    await create_task()
    scheduler.start()
    try:
        await bot.delete_webhook()
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
