from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import settings

CONTACT = "@uzbtrust"


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # event here is Message or CallbackQuery (registered per-type below)
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        else:
            return await handler(event, data)

        if user_id is None:
            return await handler(event, data)

        if user_id not in settings.allowed_ids:
            if isinstance(event, Message):
                await event.answer(
                    f"⛔ Botdan foydalanish uchun {CONTACT} ga yozing."
                )
            else:
                await event.answer(
                    f"⛔ Ruxsat yo'q. {CONTACT} ga yozing.",
                    show_alert=True,
                )
            return

        return await handler(event, data)
