from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.auth import ResendCodeRequest
from loguru import logger


_CODE_TYPE_MESSAGES = {
    "SentCodeTypeApp":        "📱 Telegram ilovasi (Telegram → «Telegram» rasmiy chati)",
    "SentCodeTypeSms":        "💬 SMS (telefoningizga)",
    "SentCodeTypeCall":       "📞 Qo'ng'iroq",
    "SentCodeTypeFlashCall":  "📞 Flash-call",
    "SentCodeTypeMissedCall": "📞 Missed call",
    "SentCodeTypeEmailCode":  "📧 Email",
    "SentCodeTypeFragment":   "🔗 Fragment.com",
}


async def send_code(client: TelegramClient, phone: str) -> tuple[str, str]:
    """Returns (phone_code_hash, delivery_hint)."""
    result = await client.send_code_request(phone)
    type_name = type(result.type).__name__
    hint = _CODE_TYPE_MESSAGES.get(type_name, f"Noma'lum ({type_name})")
    logger.info(f"Code sent to {phone} via {type_name}")
    return result.phone_code_hash, hint


async def resend_code(client: TelegramClient, phone: str, phone_code_hash: str) -> tuple[str, str]:
    """
    Ask Telegram to resend via the next method (usually SMS after App).
    Returns (new_phone_code_hash, delivery_hint).
    """
    result = await client(ResendCodeRequest(phone=phone, phone_code_hash=phone_code_hash))
    type_name = type(result.type).__name__
    hint = _CODE_TYPE_MESSAGES.get(type_name, f"Noma'lum ({type_name})")
    logger.info(f"Code RESENTto {phone} via {type_name}")
    return result.phone_code_hash, hint


async def sign_in_code(
    client: TelegramClient,
    phone: str,
    code: str,
    phone_code_hash: str,
) -> object:
    return await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)


async def sign_in_2fa(client: TelegramClient, password: str) -> object:
    return await client.sign_in(password=password)
