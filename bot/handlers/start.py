from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

import db.crud as crud
from bot.keyboards.inline import connect_account_kb, main_menu_kb
from bot.locales import t

router = Router(name="start")


async def show_main_menu(message: Message, lang: str, name: str) -> None:
    await message.answer(
        t("welcome_back", lang, name=name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    tg = message.from_user
    user, created = await crud.get_or_create_user(
        session,
        tg.id,
        tg.username,
        tg.first_name,
    )

    accounts = await crud.get_accounts(session, user.id)
    lang = user.language

    if not accounts:
        await message.answer(
            t("welcome", lang),
            reply_markup=connect_account_kb(lang),
            parse_mode="HTML",
        )
    else:
        name = tg.first_name or tg.username or str(tg.id)
        await show_main_menu(message, lang, name)


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession) -> None:
    tg = message.from_user
    user = await crud.get_user(session, tg.id)
    if not user:
        await message.answer(t("welcome", "uz"), reply_markup=connect_account_kb("uz"), parse_mode="HTML")
        return
    name = tg.first_name or tg.username or str(tg.id)
    await show_main_menu(message, user.language, name)
