from datetime import datetime

from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

import db.crud as crud
from config import settings

router = Router(name="admin")


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return (
            message.from_user is not None
            and message.from_user.id in settings.admin_id_list
        )


def _bar(value: int, max_val: int, width: int = 12) -> str:
    if max_val == 0:
        filled = 0
    else:
        filled = round(value / max_val * width)
    return "█" * filled + "░" * (width - filled)


@router.message(Command("start"), AdminFilter())
async def admin_start(message: Message, session: AsyncSession) -> None:
    try:
        stats = await crud.get_admin_stats(session)
    except Exception as e:
        await message.answer(f"❌ Xatolik: <code>{e}</code>", parse_mode="HTML")
        return
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # ── 7 kunlik yuborishlar grafigi ─────────────────────────────────────────
    days_data = stats.get("days_data", [])
    max_sends = max((d["count"] for d in days_data), default=1) or 1
    sends_chart = ""
    for d in days_data:
        bar = _bar(d["count"], max_sends)
        sends_chart += f"  {d['date']}  {bar}  {d['count']}\n"

    # ── 7 kunlik yangi foydalanuvchilar ──────────────────────────────────────
    users_data = stats.get("users_data", [])
    max_users = max((d["count"] for d in users_data), default=1) or 1
    users_chart = ""
    for d in users_data:
        bar = _bar(d["count"], max_users)
        users_chart += f"  {d['date']}  {bar}  {d['count']}\n"

    # ── Kampaniya holatlari ───────────────────────────────────────────────────
    sc = stats.get("status_counts", {})
    running = sc.get("running", 0)
    paused  = sc.get("paused",  0)
    stopped = sc.get("stopped", 0)

    text = (
        f"<b>🤖 Admin paneli</b>  |  {now}\n"
        f"{'─' * 32}\n"
        f"👤 Foydalanuvchilar:  <b>{stats['total_users']}</b>\n"
        f"📱 Akkauntlar:        <b>{stats['total_accounts']}</b>\n"
        f"👥 Guruhlar:          <b>{stats['total_groups']}</b>\n"
        f"📋 Jami kampaniyalar: <b>{stats['total_campaigns']}</b>\n"
        f"   🟢 Faol:     <b>{running}</b>  ⏸ Pauza: <b>{paused}</b>  ⏹ To'xtagan: <b>{stopped}</b>\n"
        f"📤 Jami yuborishlar:  <b>{stats['total_sent']}</b>\n"
        f"{'─' * 32}\n"
        f"<b>📊 Yuborishlar (7 kun)</b>\n"
        f"<code>{sends_chart}</code>"
        f"<b>👥 Yangi userlar (7 kun)</b>\n"
        f"<code>{users_chart}</code>"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("stats"), AdminFilter())
async def admin_stats(message: Message, session: AsyncSession) -> None:
    await admin_start(message, session)
