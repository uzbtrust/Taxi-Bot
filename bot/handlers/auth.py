from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from loguru import logger

import db.crud as crud
from bot.keyboards.inline import AccountCB, main_menu_kb
from bot.locales import t
from bot.states.fsm import AuthStates
from userbot.auth_flow import resend_code, send_code, sign_in_code, sign_in_2fa
from userbot.client_manager import client_manager
from utils.crypto import encrypt
from utils.validators import clean_code, clean_phone, is_valid_phone

router = Router(name="auth")


class ResendCB(CallbackData, prefix="resend"):
    pass


class CancelAuthCB(CallbackData, prefix="cancel_auth"):
    pass


def _code_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📵 Kod kelmadi? SMS yuborish", callback_data=ResendCB().pack())],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=CancelAuthCB().pack())],
    ])


def _cancel_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=CancelAuthCB().pack())],
    ])


async def _get_lang(session: AsyncSession, user_id: int) -> str:
    user = await crud.get_user(session, user_id)
    return user.language if user else "uz"


def _code_prompt(delivery_hint: str) -> str:
    return (
        f"📩 <b>Kod yuborildi!</b>\n\n"
        f"<b>Qayerga:</b> {delivery_hint}\n\n"
        f"Kodni bu yerga yuboring (bo'sh joy bilan):\n"
        f"<code>1 2 3 4 5</code>"
    )


# ── Trigger: "Yangi akkaunt qo'shish" button ─────────────────────────────────

@router.callback_query(AccountCB.filter(F.action == "add"))
async def cb_add_account(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    lang = await _get_lang(session, callback.from_user.id)
    await state.set_state(AuthStates.waiting_phone)
    await callback.message.edit_text(
        t("auth_enter_phone", lang),
        reply_markup=_cancel_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(CancelAuthCB.filter())
async def cb_cancel_auth(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await client_manager.remove_temp_client(callback.from_user.id)
    lang = await _get_lang(session, callback.from_user.id)
    name = callback.from_user.first_name or ""
    await callback.message.edit_text(
        t("welcome_back", lang, name=name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Step 1: Phone number ──────────────────────────────────────────────────────

@router.message(AuthStates.waiting_phone)
async def handle_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _get_lang(session, message.from_user.id)
    phone = clean_phone(message.text or "")

    if not is_valid_phone(phone):
        await message.answer(t("auth_invalid_phone", lang), parse_mode="HTML")
        return

    accounts = await crud.get_accounts(session, message.from_user.id)
    if any(acc.phone == phone for acc in accounts):
        await message.answer(t("auth_already_exists", lang), parse_mode="HTML")
        return

    status_msg = await message.answer(t("auth_sending_code", lang), parse_mode="HTML")

    try:
        client = await client_manager.get_temp_client(message.from_user.id)
        phone_code_hash, delivery_hint = await send_code(client, phone)
    except FloodWaitError as e:
        await client_manager.remove_temp_client(message.from_user.id)
        await state.clear()
        await status_msg.edit_text(t("auth_flood", lang, sec=e.seconds), parse_mode="HTML")
        return
    except PhoneNumberBannedError:
        await client_manager.remove_temp_client(message.from_user.id)
        await state.clear()
        await status_msg.edit_text(t("auth_error", lang, error="Raqam bloklangan"), parse_mode="HTML")
        return
    except Exception as e:
        logger.error(f"send_code error for {phone}: {type(e).__name__}: {e}")
        await client_manager.remove_temp_client(message.from_user.id)
        await state.clear()
        await status_msg.edit_text(
            f"❌ Kod yuborishda xatolik:\n<code>{type(e).__name__}: {e}</code>\n\n/start",
            parse_mode="HTML",
        )
        return

    await state.update_data(phone=phone, phone_code_hash=phone_code_hash)
    await state.set_state(AuthStates.waiting_code)
    await status_msg.edit_text(
        _code_prompt(delivery_hint),
        reply_markup=_code_kb(lang),
        parse_mode="HTML",
    )


# ── Resend via SMS ────────────────────────────────────────────────────────────

@router.callback_query(ResendCB.filter(), AuthStates.waiting_code)
async def cb_resend_code(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    lang = await _get_lang(session, callback.from_user.id)
    data = await state.get_data()
    phone = data.get("phone", "")
    phone_code_hash = data.get("phone_code_hash", "")

    await callback.answer("⏳ SMS yuborilmoqda...", show_alert=False)

    try:
        client = await client_manager.get_temp_client(callback.from_user.id)
        new_hash, delivery_hint = await resend_code(client, phone, phone_code_hash)
        await state.update_data(phone_code_hash=new_hash)
        logger.info(f"Code resent to {phone} via new method")
    except FloodWaitError as e:
        await callback.answer(f"⏳ {e.seconds} soniya kuting", show_alert=True)
        return
    except Exception as e:
        logger.error(f"resend_code error: {e}")
        await callback.answer(f"❌ Xatolik: {e}", show_alert=True)
        return

    await callback.message.edit_text(
        _code_prompt(delivery_hint),
        reply_markup=_code_kb(lang),
        parse_mode="HTML",
    )


# ── Step 2: Verification code ─────────────────────────────────────────────────

@router.message(AuthStates.waiting_code)
async def handle_code(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _get_lang(session, message.from_user.id)
    code = clean_code(message.text or "")
    data = await state.get_data()
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]

    try:
        client = await client_manager.get_temp_client(message.from_user.id)
        me = await sign_in_code(client, phone, code, phone_code_hash)
    except SessionPasswordNeededError:
        await state.set_state(AuthStates.waiting_2fa)
        await message.answer(t("auth_enter_2fa", lang), reply_markup=_cancel_kb(lang), parse_mode="HTML")
        return
    except (PhoneCodeInvalidError, PhoneCodeExpiredError):
        await message.answer(t("auth_wrong_code", lang), parse_mode="HTML")
        return
    except FloodWaitError as e:
        await client_manager.remove_temp_client(message.from_user.id)
        await state.clear()
        await message.answer(t("auth_flood", lang, sec=e.seconds), parse_mode="HTML")
        return
    except Exception as e:
        logger.error(f"sign_in_code error: {e}")
        await message.answer(t("auth_error", lang, error=str(e)), parse_mode="HTML")
        return

    await _finalize_auth(message, state, session, me, phone, lang)


# ── Step 3: 2FA password (optional) ──────────────────────────────────────────

@router.message(AuthStates.waiting_2fa)
async def handle_2fa(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _get_lang(session, message.from_user.id)
    password = message.text or ""

    try:
        client = await client_manager.get_temp_client(message.from_user.id)
        me = await sign_in_2fa(client, password)
    except Exception as e:
        err = str(e).lower()
        if "password" in err or "invalid" in err:
            await message.answer(t("auth_wrong_2fa", lang), parse_mode="HTML")
        else:
            await message.answer(t("auth_error", lang, error=str(e)), parse_mode="HTML")
        return

    data = await state.get_data()
    await _finalize_auth(message, state, session, me, data["phone"], lang)


# ── Finalize ──────────────────────────────────────────────────────────────────

async def _finalize_auth(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    me,
    phone: str,
    lang: str,
) -> None:
    user_id = message.from_user.id

    acc = await crud.create_account(
        session,
        user_id=user_id,
        phone=phone,
        tg_account_id=me.id,
        tg_username=me.username,
        tg_first_name=me.first_name,
        session_encrypted="__pending__",
    )

    session_str = await client_manager.promote_temp_client(user_id, acc.id)
    await crud.update_session(session, acc.id, encrypt(session_str))
    await state.clear()

    name = me.first_name or me.username or phone
    await message.answer(t("auth_success", lang, name=name, phone=phone), parse_mode="HTML")
    await message.answer(
        t("welcome_back", lang, name=name),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )
