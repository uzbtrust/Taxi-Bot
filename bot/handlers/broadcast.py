import asyncio
from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

import db.crud as crud
from bot.keyboards.inline import (
    BroadcastCB,
    MenuCB,
    ReminderCB,
    broadcast_confirm_kb,
    broadcast_menu_kb,
    campaign_detail_kb,
    campaigns_list_kb,
    cancel_kb,
    interval_kb,
    main_menu_kb,
    select_account_kb,
)
from bot.locales import t
from bot.states.fsm import BroadcastStates
from scheduler.jobs import broadcast_job, job_id, reminder_job, reminder_job_id
from scheduler.scheduler import scheduler

router = Router(name="broadcast")


async def _lang(session: AsyncSession, user_id: int) -> str:
    user = await crud.get_user(session, user_id)
    return user.language if user else "uz"


async def _show_broadcast_menu(
    callback: CallbackQuery,
    account_id: int,
    session: AsyncSession,
    lang: str,
) -> None:
    campaigns = await crud.get_campaigns_by_account(session, account_id)
    await callback.message.edit_text(
        t("broadcast_menu", lang),
        reply_markup=broadcast_menu_kb(len(campaigns), account_id, lang),
        parse_mode="HTML",
    )


# ── Entry point ───────────────────────────────────────────────────────────────

@router.callback_query(MenuCB.filter(F.section == "broadcast"))
async def cb_broadcast_menu(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    accounts = await crud.get_accounts(session, callback.from_user.id)
    active_accounts = [a for a in accounts if a.is_active]

    if not active_accounts:
        await callback.answer(t("broadcast_no_accounts", lang), show_alert=True)
        return

    await state.clear()

    if len(active_accounts) == 1:
        await _show_broadcast_menu(callback, active_accounts[0].id, session, lang)
    else:
        await callback.message.edit_text(
            t("select_account_for_broadcast", lang),
            reply_markup=select_account_kb(active_accounts, "broadcast", lang),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(BroadcastCB.filter(F.action == "select_account"))
async def cb_select_account(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    await _show_broadcast_menu(callback, callback_data.account_id, session, lang)
    await callback.answer()


@router.callback_query(BroadcastCB.filter(F.action == "menu"))
async def cb_back_to_menu(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    await _show_broadcast_menu(callback, callback_data.account_id, session, lang)
    await callback.answer()


# ── New message flow ──────────────────────────────────────────────────────────

@router.callback_query(BroadcastCB.filter(F.action == "new_message"))
async def cb_new_message(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    groups = await crud.get_active_groups(session, callback_data.account_id)
    if not groups:
        await callback.answer(t("broadcast_no_groups", lang), show_alert=True)
        return

    await state.set_state(BroadcastStates.waiting_message)
    await state.update_data(account_id=callback_data.account_id)
    await callback.message.edit_text(
        t("broadcast_enter_message", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BroadcastStates.waiting_message)
async def handle_broadcast_message(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, message.from_user.id)
    text = (message.text or message.caption or "").strip()
    if not text:
        await message.answer("❌ Faqat matnli habar yuboring.", parse_mode="HTML")
        return
    if len(text) > 4096:
        await message.answer("❌ Habar juda uzun (max 4096 belgi).", parse_mode="HTML")
        return

    data = await state.get_data()
    account_id: int = data.get("account_id", 0)
    acc = await crud.get_account(session, account_id)
    if not acc:
        await state.clear()
        await message.answer(t("error_generic", lang), parse_mode="HTML")
        return

    await state.update_data(message_text=text)
    await state.set_state(BroadcastStates.confirming)
    await message.answer(
        t("select_interval", lang),
        reply_markup=interval_kb(account_id, lang),
        parse_mode="HTML",
    )


@router.callback_query(BroadcastCB.filter(F.action == "set_interval"))
async def cb_set_interval(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    data = await state.get_data()
    text: str = data.get("message_text", "")
    account_id = callback_data.account_id
    minutes = callback_data.minutes

    acc = await crud.get_account(session, account_id)
    if not acc:
        await callback.answer(t("error_generic", lang), show_alert=True)
        return

    groups = await crud.get_active_groups(session, account_id)
    if not groups:
        await callback.answer(t("broadcast_no_groups", lang), show_alert=True)
        return

    acc_name = acc.tg_first_name or acc.tg_username or acc.phone
    preview = text[:80] + ("..." if len(text) > 80 else "")

    await state.update_data(minutes=minutes)
    await callback.message.edit_text(
        t("broadcast_preview", lang,
          text=preview,
          groups=len(groups),
          interval=minutes,
          account=acc_name),
        reply_markup=broadcast_confirm_kb(account_id, minutes, lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BroadcastCB.filter(F.action == "start"))
async def cb_start_broadcast(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    data = await state.get_data()
    text: str = data.get("message_text", "")
    account_id = callback_data.account_id
    minutes = callback_data.minutes

    groups = await crud.get_active_groups(session, account_id)
    if not groups:
        await callback.answer(t("broadcast_no_groups", lang), show_alert=True)
        return

    user_tg_id = callback.from_user.id
    campaign = await crud.create_campaign(session, account_id, user_tg_id, text, minutes)
    await state.clear()

    scheduler.add_job(
        broadcast_job,
        trigger="interval",
        minutes=minutes,
        id=job_id(campaign.id),
        kwargs={"campaign_id": campaign.id, "user_tg_id": user_tg_id},
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        reminder_job,
        trigger="interval",
        hours=1,
        id=reminder_job_id(campaign.id),
        kwargs={"campaign_id": campaign.id, "user_tg_id": user_tg_id},
        replace_existing=True,
        max_instances=1,
    )

    asyncio.create_task(broadcast_job(campaign.id, user_tg_id))

    preview = text[:60] + ("..." if len(text) > 60 else "")
    started = (campaign.created_at + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
    campaigns = await crud.get_campaigns_by_account(session, account_id)
    num = next((i + 1 for i, c in enumerate(campaigns) if c.id == campaign.id), len(campaigns))

    await callback.message.edit_text(
        t("campaign_detail", lang,
          num=num,
          text=preview,
          interval=minutes,
          sent=0,
          failed=0,
          groups=len(groups),
          started=started),
        reply_markup=campaign_detail_kb(campaign.id, account_id, lang),
        parse_mode="HTML",
    )
    await callback.answer(t("broadcast_started_alert", lang, interval=minutes, groups=len(groups)), show_alert=True)


# ── Active campaigns list ─────────────────────────────────────────────────────

@router.callback_query(BroadcastCB.filter(F.action == "active_list"))
async def cb_active_list(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    campaigns = await crud.get_campaigns_by_account(session, callback_data.account_id)
    if not campaigns:
        await callback.message.edit_text(
            t("campaigns_empty", lang),
            reply_markup=broadcast_menu_kb(0, callback_data.account_id, lang),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    header, kb = campaigns_list_kb(campaigns, callback_data.account_id, lang)
    await callback.message.edit_text(header, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(BroadcastCB.filter(F.action == "detail"))
async def cb_campaign_detail(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    campaign = await crud.get_campaign(session, callback_data.campaign_id)
    if not campaign:
        await callback.answer("Topilmadi", show_alert=True)
        return

    campaigns = await crud.get_campaigns_by_account(session, campaign.account_id)
    num = next((i + 1 for i, c in enumerate(campaigns) if c.id == campaign.id), 1)
    groups = await crud.get_active_groups(session, campaign.account_id)
    preview = campaign.message_text[:60] + ("..." if len(campaign.message_text) > 60 else "")
    started = (campaign.created_at + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")

    await callback.message.edit_text(
        t("campaign_detail", lang,
          num=num,
          text=preview,
          interval=campaign.interval_minutes,
          sent=campaign.total_sent,
          failed=campaign.total_failed,
          groups=len(groups),
          started=started),
        reply_markup=campaign_detail_kb(campaign.id, campaign.account_id, lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Delete campaign ───────────────────────────────────────────────────────────

@router.callback_query(BroadcastCB.filter(F.action == "delete_confirm"))
async def cb_delete_confirm(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    campaign = await crud.get_campaign(session, callback_data.campaign_id)
    if not campaign:
        await callback.answer("Topilmadi", show_alert=True)
        return

    campaigns = await crud.get_campaigns_by_account(session, campaign.account_id)
    num = next((i + 1 for i, c in enumerate(campaigns) if c.id == campaign.id), 1)

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn_confirm_delete", lang),
                callback_data=BroadcastCB(action="delete", campaign_id=campaign.id, account_id=callback_data.account_id).pack(),
            ),
            InlineKeyboardButton(
                text=t("btn_no", lang),
                callback_data=BroadcastCB(action="detail", campaign_id=campaign.id, account_id=callback_data.account_id).pack(),
            ),
        ]
    ])
    await callback.message.edit_text(
        t("campaign_delete_confirm", lang, num=num),
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BroadcastCB.filter(F.action == "delete"))
async def cb_delete_campaign(
    callback: CallbackQuery,
    callback_data: BroadcastCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    campaign_id = callback_data.campaign_id
    account_id = callback_data.account_id

    try:
        scheduler.remove_job(job_id(campaign_id))
    except Exception:
        pass
    try:
        scheduler.remove_job(reminder_job_id(campaign_id))
    except Exception:
        pass

    await crud.delete_campaign(session, campaign_id)
    await callback.answer(t("campaign_deleted", lang), show_alert=True)

    campaigns = await crud.get_campaigns_by_account(session, account_id)
    if not campaigns:
        await callback.message.edit_text(
            t("broadcast_menu", lang),
            reply_markup=broadcast_menu_kb(0, account_id, lang),
            parse_mode="HTML",
        )
    else:
        header, kb = campaigns_list_kb(campaigns, account_id, lang)
        await callback.message.edit_text(header, reply_markup=kb, parse_mode="HTML")


# ── Hourly reminder response ──────────────────────────────────────────────────

@router.callback_query(ReminderCB.filter(F.action == "yes"))
async def cb_reminder_yes(
    callback: CallbackQuery,
    callback_data: ReminderCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    await callback.answer(t("reminder_continued", lang), show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        pass


@router.callback_query(ReminderCB.filter(F.action == "no"))
async def cb_reminder_no(
    callback: CallbackQuery,
    callback_data: ReminderCB,
    session: AsyncSession,
) -> None:
    lang = await _lang(session, callback.from_user.id)
    campaign_id = callback_data.campaign_id

    try:
        scheduler.remove_job(job_id(campaign_id))
    except Exception:
        pass
    try:
        scheduler.remove_job(reminder_job_id(campaign_id))
    except Exception:
        pass

    await crud.delete_campaign(session, campaign_id)
    await callback.answer(t("reminder_stopped", lang), show_alert=True)
    try:
        await callback.message.delete()
    except Exception:
        pass
