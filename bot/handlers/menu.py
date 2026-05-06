from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import db.crud as crud
from bot.keyboards.inline import MenuCB, main_menu_kb, settings_kb, back_to_main_kb
from bot.locales import t

router = Router(name="menu")


async def _lang(session: AsyncSession, user_id: int) -> str:
    user = await crud.get_user(session, user_id)
    return user.language if user else "uz"


@router.callback_query(MenuCB.filter(F.section == "main"))
async def cb_main_menu(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    lang = await _lang(session, callback.from_user.id)
    user = await crud.get_user(session, callback.from_user.id)
    name = callback.from_user.first_name or callback.from_user.username or ""
    await callback.message.edit_text(
        t("welcome_back", lang, name=name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(MenuCB.filter(F.section == "settings"))
async def cb_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback.from_user.id)
    lang_name = "O'zbek" if lang == "uz" else "Русский"
    await callback.message.edit_text(
        t("settings_menu", lang, lang=lang_name),
        reply_markup=settings_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(MenuCB.filter(F.section == "help"))
async def cb_help(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback.from_user.id)
    await callback.message.edit_text(
        t("help_text", lang),
        reply_markup=back_to_main_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()
