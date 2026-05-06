import asyncio
import random

from loguru import logger
from telethon import TelegramClient
from telethon.errors import (
    ChatWriteForbiddenError,
    FloodWaitError,
    SlowModeWaitError,
    UserBannedInChannelError,
    UserDeactivatedBanError,
    ChatIdInvalidError,
    ChannelPrivateError,
)

from db.models import Group

# Decorative suffixes rotated per send to look more human
_SUFFIXES = ["", " 🚗", " ✅", " 🚕", " 📞", ""]


async def send_to_groups(
    client: TelegramClient,
    groups: list[Group],
    text: str,
    suffix_index: int = 0,
) -> tuple[list[int], list[tuple[int, str]]]:
    """
    Send `text` to all groups.
    Returns (ok_group_ids, [(failed_group_id, reason), ...]).
    Adds small random delay between sends.
    """
    suffix = _SUFFIXES[suffix_index % len(_SUFFIXES)]
    message = text + suffix

    ok: list[int] = []
    failed: list[tuple[int, str]] = []

    for grp in groups:
        try:
            await client.send_message(grp.chat_id, message)
            ok.append(grp.id)
            logger.debug(f"Sent to {grp.title} ({grp.chat_id})")
            await asyncio.sleep(random.uniform(2, 5))

        except FloodWaitError as e:
            logger.warning(f"FloodWait {e.seconds}s for group {grp.title}")
            failed.append((grp.id, f"flood:{e.seconds}"))

        except SlowModeWaitError as e:
            logger.warning(f"SlowMode {e.seconds}s for {grp.title}")
            failed.append((grp.id, f"slowmode:{e.seconds}"))

        except (ChatWriteForbiddenError, UserBannedInChannelError):
            logger.warning(f"Forbidden/banned in {grp.title}")
            failed.append((grp.id, "forbidden"))

        except (ChannelPrivateError, ChatIdInvalidError):
            logger.warning(f"Group no longer accessible: {grp.title}")
            failed.append((grp.id, "inaccessible"))

        except UserDeactivatedBanError:
            logger.error("Account banned!")
            failed.append((grp.id, "account_banned"))
            break  # No point continuing with a banned account

        except Exception as e:
            logger.error(f"Unexpected error sending to {grp.title}: {e}")
            failed.append((grp.id, f"error:{type(e).__name__}"))

    return ok, failed
