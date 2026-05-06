from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import db.crud as crud
from bot.keyboards.inline import SettingsCB, main_menu_kb, settings_kb
from bot.locales import t

router = Router(name="settings")


@router.callback_query(SettingsCB.filter(F.action.in_(["lang_uz", "lang_ru"])))
async def cb_change_lang(
    callback: CallbackQuery,
    callback_data: SettingsCB,
    session: AsyncSession,
) -> None:
    lang = "uz" if callback_data.action == "lang_uz" else "ru"
    await crud.set_language(session, callback.from_user.id, lang)
    lang_name = "O'zbek" if lang == "uz" else "Русский"
    await callback.answer(t("lang_changed", lang, lang=lang_name), show_alert=True)

    await callback.message.edit_text(
        t("settings_menu", lang, lang=lang_name),
        reply_markup=settings_kb(lang),
        parse_mode="HTML",
    )
