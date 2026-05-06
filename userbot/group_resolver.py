import re

from telethon import TelegramClient
from telethon.errors import (
    ChatAdminRequiredError,
    ChannelPrivateError,
    InviteHashExpiredError,
    InviteHashInvalidError,
    UserAlreadyParticipantError,
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel, Chat

from loguru import logger


def extract_invite_hash(link: str) -> str | None:
    patterns = [
        r"t\.me/\+([A-Za-z0-9_-]+)",
        r"t\.me/joinchat/([A-Za-z0-9_-]+)",
        r"telegram\.me/joinchat/([A-Za-z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, link)
        if m:
            return m.group(1)
    return None


async def resolve_by_username(
    client: TelegramClient, username: str
) -> tuple[int, str, str | None]:
    """
    Returns (chat_id, title, username).
    Joins if not already a member.
    Raises ChannelPrivateError if private.
    """
    entity = await client.get_entity(username)
    chat_id = entity.id
    title = getattr(entity, "title", str(chat_id))
    uname = getattr(entity, "username", None)

    if isinstance(entity, (Channel, Chat)):
        try:
            await client(JoinChannelRequest(entity))
            logger.info(f"Joined group: {title}")
        except UserAlreadyParticipantError:
            pass

    return chat_id, title, uname


async def resolve_by_invite(
    client: TelegramClient, link: str
) -> tuple[int, str, None]:
    """
    Returns (chat_id, title, None) for private groups.
    Raises InviteHashExpiredError / InviteHashInvalidError on bad link.
    """
    invite_hash = extract_invite_hash(link)
    if not invite_hash:
        raise ValueError("Cannot extract invite hash from link")

    try:
        result = await client(ImportChatInviteRequest(invite_hash))
        chat = result.chats[0]
        return chat.id, getattr(chat, "title", str(chat.id)), None
    except UserAlreadyParticipantError:
        # Already in group — resolve entity to get chat_id
        info = await client.get_entity(invite_hash)
        return info.id, getattr(info, "title", str(info.id)), None
