from datetime import datetime

from loguru import logger

import db.base as db_base
import db.crud as crud
from userbot.client_manager import client_manager
from userbot.sender import send_to_groups

_round_counters: dict[int, int] = {}

_bot = None


def set_bot(bot) -> None:
    global _bot
    _bot = bot


def job_id(campaign_id: int) -> str:
    return f"campaign_{campaign_id}"


def reminder_job_id(campaign_id: int) -> str:
    return f"reminder_{campaign_id}"


async def broadcast_job(campaign_id: int, user_tg_id: int) -> None:
    async with db_base.AsyncSessionFactory() as session:
        campaign = await crud.get_campaign(session, campaign_id)
        if not campaign or campaign.status != "running":
            return

        account = await crud.get_account(session, campaign.account_id)
        if not account or not account.is_active:
            return

        groups = await crud.get_active_groups(session, account.id)
        if not groups:
            logger.warning(f"No active groups for campaign {campaign_id}")
            return

        try:
            telethon_client = await client_manager.get_client(account.id, account.session_encrypted)
        except Exception as e:
            logger.error(f"Cannot get client for account {account.id}: {e}")
            return

        round_num = _round_counters.get(campaign_id, 0)
        _round_counters[campaign_id] = round_num + 1

        ok_ids, failed = await send_to_groups(telethon_client, groups, campaign.message_text, round_num)

        if ok_ids:
            await crud.increment_campaign_sent(session, campaign_id, len(ok_ids))
        if failed:
            await crud.increment_campaign_failed(session, campaign_id, len(failed))

        for gid in ok_ids:
            grp = next((g for g in groups if g.id == gid), None)
            await crud.create_send_log(session, campaign_id, gid, getattr(grp, "title", None), "ok")

        for gid, reason in failed:
            grp = next((g for g in groups if g.id == gid), None)
            gtitle = getattr(grp, "title", None)
            await crud.create_send_log(session, campaign_id, gid, gtitle, reason.split(":")[0], reason)



async def reminder_job(campaign_id: int, user_tg_id: int) -> None:
    """Sends hourly reminder asking if broadcast should continue."""
    async with db_base.AsyncSessionFactory() as session:
        campaign = await crud.get_campaign(session, campaign_id)
        if not campaign or campaign.status != "running":
            return

        hours = max(1, int((datetime.utcnow() - campaign.created_at).total_seconds() / 3600))
        preview = campaign.message_text[:60] + ("..." if len(campaign.message_text) > 60 else "")

        if not _bot:
            return

        from bot.locales import t
        from bot.keyboards.inline import reminder_kb

        user = await crud.get_user(session, user_tg_id)
        lang = user.language if user else "uz"

        try:
            await _bot.send_message(
                user_tg_id,
                t("reminder_text", lang, hours=hours, text=preview),
                reply_markup=reminder_kb(campaign_id, lang),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send reminder for campaign {campaign_id}: {e}")
