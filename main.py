import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config import settings
from db.base import init_db
import db.base as db_base
from scheduler.scheduler import scheduler
from scheduler.jobs import set_bot, broadcast_job, reminder_job, job_id, reminder_job_id
from bot.middlewares.db import DatabaseMiddleware
from bot.middlewares.access import AccessMiddleware
from bot.handlers import (
    admin_router,
    start_router,
    auth_router,
    menu_router,
    accounts_router,
    groups_router,
    broadcast_router,
)
from utils.logger import setup_logger
import db.crud as crud


async def restore_campaigns(bot: Bot) -> None:
    async with db_base.AsyncSessionFactory() as session:
        campaigns = await crud.get_all_running_campaigns(session)
        for camp in campaigns:
            user = await crud.get_user(session, camp.account.user_id)
            if not user:
                continue
            user_tg_id = camp.user_tg_id or user.id
            scheduler.add_job(
                broadcast_job,
                trigger="interval",
                minutes=camp.interval_minutes,
                id=job_id(camp.id),
                kwargs={"campaign_id": camp.id, "user_tg_id": user_tg_id},
                replace_existing=True,
                max_instances=1,
            )
            scheduler.add_job(
                reminder_job,
                trigger="interval",
                hours=1,
                id=reminder_job_id(camp.id),
                kwargs={"campaign_id": camp.id, "user_tg_id": user_tg_id},
                replace_existing=True,
                max_instances=1,
            )
            logger.info(f"Restored campaign {camp.id} (every {camp.interval_minutes} min)")


async def health_server() -> None:
    """Minimal HTTP server for Back4App health check on port 8080."""
    from aiohttp import web

    async def handle(_):
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()


async def main() -> None:
    os.makedirs("logs", exist_ok=True)
    setup_logger()
    logger.info("Starting Taxi Auto Bot...")

    await init_db(settings.database_url)
    logger.info("Database initialized")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Access check — per message/callback so event type is correct
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

    # DB session injection for all update types
    dp.update.middleware(DatabaseMiddleware())

    # Admin router first — takes priority on /start for admins
    dp.include_routers(
        admin_router,
        start_router,
        auth_router,
        menu_router,
        accounts_router,
        groups_router,
        broadcast_router,
    )

    set_bot(bot)
    scheduler.start()
    logger.info("Scheduler started")

    from userbot.client_manager import client_manager
    client_manager.start_idle_sweeper()

    await restore_campaigns(bot)

    await health_server()
    logger.info("Bot is running. Press Ctrl+C to stop.")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await client_manager.disconnect_all()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
