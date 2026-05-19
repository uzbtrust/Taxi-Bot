from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import db.crud as crud
from bot.keyboards.inline import (
    AccountCB,
    MenuCB,
    account_detail_kb,
    accounts_list_kb,
    delete_confirm_kb,
    main_menu_kb,
)
from bot.locales import t
from userbot.client_manager import client_manager

router = Router(name="accounts")


async def _lang(session: AsyncSession, user_id: int) -> str:
    user = await crud.get_user(session, user_id)
    return user.language if user else "uz"


async def _show_accounts_list(callback: CallbackQuery, session: AsyncSession, lang: str) -> None:
    accounts = await crud.get_accounts(session, callback.from_user.id)
    if not accounts:
        await callback.message.edit_text(
            t("accounts_empty", lang),
            reply_markup=__import__("bot.keyboards.inline", fromlist=["connect_account_kb"]).connect_account_kb(lang),
            parse_mode="HTML",
        )
        return

    lines = []
    for acc in accounts:
        icon = t("account_active", lang) if acc.is_active else t("account_paused", lang)
        name = acc.tg_first_name or acc.tg_username or acc.phone
        groups = await crud.get_groups(session, acc.id)
        lines.append(t("account_item", lang, icon=icon, name=name, phone=acc.phone, groups=len(groups)))

    text = t("accounts_list", lang, count=len(accounts)) + "\n\n" + "\n\n".join(lines)
    await callback.message.edit_text(
        text,
        reply_markup=accounts_list_kb(accounts, lang),
        parse_mode="HTML",
    )


@router.callback_query(MenuCB.filter(F.section == "accounts"))
async def cb_accounts_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback.from_user.id)
    await _show_accounts_list(callback, session, lang)
    await callback.answer()


@router.callback_query(AccountCB.filter(F.action == "view"))
async def cb_account_view(
    callback: CallbackQuery,
    callback_data: AccountCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    acc = await crud.get_account(session, callback_data.account_id)
    if not acc:
        await callback.answer("Topilmadi", show_alert=True)
        return

    name = acc.tg_first_name or acc.tg_username or acc.phone
    icon = t("account_active", lang) if acc.is_active else t("account_paused", lang)
    groups = await crud.get_groups(session, acc.id)
    campaign = await crud.get_running_campaign(session, acc.id)

    text = (
        f"{icon} <b>{name}</b>\n"
        f"📱 Telefon: <code>{acc.phone}</code>\n"
        f"👥 Guruhlar: <b>{len(groups)}</b> ta\n"
        f"📋 Kampaniya: <b>{'Faol' if campaign else 'Yoq'}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=account_detail_kb(acc.id, acc.is_active, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(AccountCB.filter(F.action == "toggle"))
async def cb_account_toggle(
    callback: CallbackQuery,
    callback_data: AccountCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    is_active = await crud.toggle_account(session, callback_data.account_id)
    msg = t("account_toggled_on", lang) if is_active else t("account_toggled_off", lang)
    await callback.answer(msg, show_alert=True)
    # Refresh view
    acc = await crud.get_account(session, callback_data.account_id)
    if acc:
        name = acc.tg_first_name or acc.tg_username or acc.phone
        icon = t("account_active", lang) if acc.is_active else t("account_paused", lang)
        groups = await crud.get_groups(session, acc.id)
        campaign = await crud.get_running_campaign(session, acc.id)
        text = (
            f"{icon} <b>{name}</b>\n"
            f"📱 Telefon: <code>{acc.phone}</code>\n"
            f"👥 Guruhlar: <b>{len(groups)}</b> ta\n"
            f"📋 Kampaniya: <b>{'Faol' if campaign else 'Yoq'}</b>"
        )
        await callback.message.edit_text(
            text,
            reply_markup=account_detail_kb(acc.id, acc.is_active, lang),
            parse_mode="HTML",
        )


@router.callback_query(AccountCB.filter(F.action == "delete_confirm"))
async def cb_account_delete_confirm(
    callback: CallbackQuery,
    callback_data: AccountCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    acc = await crud.get_account(session, callback_data.account_id)
    if not acc:
        await callback.answer("Topilmadi", show_alert=True)
        return
    name = acc.tg_first_name or acc.tg_username or acc.phone
    await callback.message.edit_text(
        t("delete_confirm", lang, name=name),
        reply_markup=delete_confirm_kb(acc.id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(AccountCB.filter(F.action == "delete"))
async def cb_account_delete(
    callback: CallbackQuery,
    callback_data: AccountCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    acc_id = callback_data.account_id

    # Stop client if running
    await client_manager.remove_client(acc_id)

    await crud.delete_account(session, acc_id)
    await callback.answer(t("account_deleted", lang), show_alert=True)
    await _show_accounts_list(callback, session, lang)
