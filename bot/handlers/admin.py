import asyncio
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import BufferedInputFile, Message
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


def _build_chart(stats: dict) -> bytes:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#1a1a2e")

    bar_col  = "#0f3460"
    bar_col2 = "#533483"
    txt_col  = "#e0e0e0"
    bg_col   = "#16213e"
    grid_col = "#333355"

    # ── Chart 1: Messages sent last 7 days ────────────────────────────────────
    ax1 = axes[0]
    ax1.set_facecolor(bg_col)
    days   = [d["date"]  for d in stats["days_data"]]
    counts = [d["count"] for d in stats["days_data"]]
    bars = ax1.bar(days, counts, color=bar_col, width=0.6, zorder=3)
    for bar, val in zip(bars, counts):
        if val > 0:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(val), ha="center", va="bottom",
                fontsize=9, color=txt_col,
            )
    ax1.set_title("Yuborishlar (7 kun)", color=txt_col, fontsize=11, pad=10)
    ax1.tick_params(colors=txt_col, labelsize=8)
    ax1.grid(axis="y", color=grid_col, linestyle="--", alpha=0.5, zorder=0)
    for sp in ax1.spines.values():
        sp.set_color(grid_col)
    ax1.set_ylim(0, max(counts + [1]) * 1.2)

    # ── Chart 2: New users last 7 days ────────────────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor(bg_col)
    udays   = [d["date"]  for d in stats["users_data"]]
    ucounts = [d["count"] for d in stats["users_data"]]
    bars2 = ax2.bar(udays, ucounts, color=bar_col2, width=0.6, zorder=3)
    for bar, val in zip(bars2, ucounts):
        if val > 0:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                str(val), ha="center", va="bottom",
                fontsize=9, color=txt_col,
            )
    ax2.set_title("Yangi foydalanuvchilar (7 kun)", color=txt_col, fontsize=11, pad=10)
    ax2.tick_params(colors=txt_col, labelsize=8)
    ax2.grid(axis="y", color=grid_col, linestyle="--", alpha=0.5, zorder=0)
    for sp in ax2.spines.values():
        sp.set_color(grid_col)
    ax2.set_ylim(0, max(ucounts + [1]) * 1.2)

    # ── Chart 3: Campaign status pie ─────────────────────────────────────────
    ax3 = axes[2]
    ax3.set_facecolor(bg_col)
    status_map = {
        "running": ("Faol",      "#2ecc71"),
        "paused":  ("Pauza",     "#f39c12"),
        "stopped": ("Toxtatilgan","#e74c3c"),
    }
    sc = stats.get("status_counts", {})
    labels, sizes, colors = [], [], []
    for key, (label, color) in status_map.items():
        if key in sc and sc[key] > 0:
            labels.append(f"{label} ({sc[key]})")
            sizes.append(sc[key])
            colors.append(color)

    if sizes:
        _, _, autotexts = ax3.pie(
            sizes, labels=None, colors=colors,
            autopct="%1.0f%%", startangle=90,
            wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 2},
        )
        for at in autotexts:
            at.set_color(txt_col)
            at.set_fontsize(9)
        patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors, labels)]
        ax3.legend(
            handles=patches, loc="lower center",
            bbox_to_anchor=(0.5, -0.15),
            fontsize=8, frameon=False, labelcolor=txt_col,
        )
    else:
        ax3.text(0, 0, "Ma'lumot yo'q", ha="center", va="center",
                 color=txt_col, fontsize=12)
        ax3.set_xlim(-1, 1)
        ax3.set_ylim(-1, 1)
    ax3.set_title("Kampaniya holatlari", color=txt_col, fontsize=11, pad=10)

    fig.suptitle(
        f"Taxi Auto Bot  |  {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        color=txt_col, fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130,
                bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


@router.message(Command("start"), AdminFilter())
async def admin_start(message: Message, session: AsyncSession) -> None:
    stats = await crud.get_admin_stats(session)

    text = (
        "<b>Admin paneli</b>\n"
        f"{'─' * 28}\n"
        f"Foydalanuvchilar:    <b>{stats['total_users']}</b>\n"
        f"Akkauntlar:          <b>{stats['total_accounts']}</b>\n"
        f"Guruhlar:            <b>{stats['total_groups']}</b>\n"
        f"Jami kampaniyalar:   <b>{stats['total_campaigns']}</b>\n"
        f"Faol kampaniyalar:   <b>{stats['active_campaigns']}</b>\n"
        f"Jami yuborishlar:    <b>{stats['total_sent']}</b>\n"
        f"{'─' * 28}\n"
        f"{datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    await message.answer(text, parse_mode="HTML")

    chart_bytes = await asyncio.to_thread(_build_chart, stats)
    photo = BufferedInputFile(chart_bytes, filename="stats.png")
    await message.answer_photo(photo, caption="<b>Grafik statistika</b>", parse_mode="HTML")


@router.message(Command("stats"), AdminFilter())
async def admin_stats(message: Message, session: AsyncSession) -> None:
    await admin_start(message, session)
