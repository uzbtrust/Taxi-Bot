from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

import db.crud as crud
from bot.keyboards.inline import (
    GroupCB,
    MenuCB,
    cancel_kb,
    group_delete_confirm_kb,
    groups_list_kb,
    select_account_kb,
)
from bot.locales import t
from bot.states.fsm import GroupStates
from userbot.client_manager import client_manager
from userbot.group_resolver import resolve_by_invite, resolve_by_username
from utils.validators import parse_group_input

router = Router(name="groups")


async def _lang(session: AsyncSession, user_id: int) -> str:
    user = await crud.get_user(session, user_id)
    return user.language if user else "uz"


def _add_back_kb(account_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_add_group", lang), callback_data=GroupCB(action="add", account_id=account_id).pack())],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack())],
    ])


@router.callback_query(MenuCB.filter(F.section == "groups"))
async def cb_groups_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    lang = await _lang(session, callback.from_user.id)
    accounts = await crud.get_accounts(session, callback.from_user.id)
    if not accounts:
        await callback.answer(t("broadcast_no_accounts", lang), show_alert=True)
        return

    if len(accounts) == 1:
        groups = await crud.get_groups(session, accounts[0].id)
        if not groups:
            await callback.message.edit_text(
                t("groups_empty", lang),
                reply_markup=_add_back_kb(accounts[0].id, lang),
                parse_mode="HTML",
            )
            await callback.answer()
            return
        header, kb = groups_list_kb(groups, accounts[0].id, 0, lang)
        await callback.message.edit_text(header, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.edit_text(
            t("select_account_for_groups", lang),
            reply_markup=select_account_kb(accounts, "groups", lang),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(GroupCB.filter(F.action == "noop"))
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(GroupCB.filter(F.action == "list"))
async def cb_groups_list(
    callback: CallbackQuery,
    callback_data: GroupCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    groups = await crud.get_groups(session, callback_data.account_id)
    if not groups:
        await callback.message.edit_text(
            t("groups_empty", lang),
            reply_markup=_add_back_kb(callback_data.account_id, lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    header, kb = groups_list_kb(groups, callback_data.account_id, callback_data.page, lang)
    await callback.message.edit_text(header, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(GroupCB.filter(F.action == "add"))
async def cb_add_group(
    callback: CallbackQuery,
    callback_data: GroupCB,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    await state.set_state(GroupStates.waiting_input)
    await state.update_data(account_id=callback_data.account_id)
    await callback.message.edit_text(
        t("groups_enter_input", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(GroupStates.waiting_input)
async def handle_group_input(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, message.from_user.id)
    data = await state.get_data()
    account_id: int = data.get("account_id", 0)

    kind, value = parse_group_input(message.text or "")
    if kind == "unknown":
        await message.answer(t("group_invalid_input", lang), parse_mode="HTML")
        return

    status_msg = await message.answer(t("group_resolving", lang), parse_mode="HTML")

    acc = await crud.get_account(session, account_id)
    if not acc:
        await state.clear()
        await status_msg.edit_text(t("error_generic", lang), parse_mode="HTML")
        return

    try:
        client = await client_manager.get_client(acc.id, acc.session_encrypted)
    except Exception as e:
        await state.clear()
        await status_msg.edit_text(t("auth_error", lang, error=str(e)), parse_mode="HTML")
        return

    try:
        if kind == "invite":
            await status_msg.edit_text(t("group_joining", lang), parse_mode="HTML")
            chat_id, title, username = await resolve_by_invite(client, value)
        else:
            await status_msg.edit_text(t("group_joining", lang), parse_mode="HTML")
            chat_id, title, username = await resolve_by_username(client, value)
    except Exception as e:
        err_str = str(e).lower()
        if "private" in err_str or "forbidden" in err_str:
            await status_msg.edit_text(t("group_private_hint", lang), parse_mode="HTML")
        elif "not found" in err_str or "invalid" in err_str or "hash" in err_str:
            await status_msg.edit_text(t("group_not_found", lang), parse_mode="HTML")
        else:
            await status_msg.edit_text(t("group_join_error", lang, error=str(e)), parse_mode="HTML")
        logger.warning(f"Group resolve failed: {e}")
        return

    if await crud.group_exists(session, account_id, chat_id):
        await state.clear()
        await status_msg.edit_text(t("group_already_exists", lang), parse_mode="HTML")
        return

    invite_link = value if kind == "invite" else None
    await crud.create_group(session, account_id, chat_id, title, username, invite_link)
    await state.clear()

    await status_msg.edit_text(t("group_added", lang, title=title), parse_mode="HTML")

    groups = await crud.get_groups(session, account_id)
    header, kb = groups_list_kb(groups, account_id, 0, lang)
    await message.answer(header, reply_markup=kb, parse_mode="HTML")


@router.callback_query(GroupCB.filter(F.action == "delete_confirm"))
async def cb_group_delete_confirm(
    callback: CallbackQuery,
    callback_data: GroupCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    grp = await crud.get_group(session, callback_data.group_id)
    if not grp:
        await callback.answer("Topilmadi", show_alert=True)
        return
    await callback.message.edit_text(
        f"🗑 <b>{grp.title}</b> guruhini o'chirmoqchimisiz?",
        reply_markup=group_delete_confirm_kb(grp.id, callback_data.account_id, callback_data.page, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(GroupCB.filter(F.action == "delete"))
async def cb_group_delete(
    callback: CallbackQuery,
    callback_data: GroupCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    await crud.delete_group(session, callback_data.group_id)
    await callback.answer(t("group_deleted", lang), show_alert=True)

    groups = await crud.get_groups(session, callback_data.account_id)
    if not groups:
        await callback.message.edit_text(
            t("groups_empty", lang),
            reply_markup=_add_back_kb(callback_data.account_id, lang),
            parse_mode="HTML",
        )
        return
    page = min(callback_data.page, max(0, (len(groups) - 1) // 8))
    header, kb = groups_list_kb(groups, callback_data.account_id, page, lang)
    await callback.message.edit_text(header, reply_markup=kb, parse_mode="HTML")
