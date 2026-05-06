from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import t
from db.models import Account, Campaign, Group


# ── Callback factories ────────────────────────────────────────────────────────

class MenuCB(CallbackData, prefix="menu"):
    section: str


class AccountCB(CallbackData, prefix="acc"):
    action: str
    account_id: int = 0


class GroupCB(CallbackData, prefix="grp"):
    action: str
    group_id: int = 0
    account_id: int = 0
    page: int = 0


class BroadcastCB(CallbackData, prefix="bc"):
    action: str
    campaign_id: int = 0
    minutes: int = 0
    account_id: int = 0


class ReminderCB(CallbackData, prefix="rem"):
    action: str
    campaign_id: int = 0


class SettingsCB(CallbackData, prefix="set"):
    action: str


# ── Keyboards ─────────────────────────────────────────────────────────────────

def main_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("btn_accounts", lang), callback_data=MenuCB(section="accounts").pack()))
    builder.row(InlineKeyboardButton(text=t("btn_groups", lang), callback_data=MenuCB(section="groups").pack()))
    builder.row(InlineKeyboardButton(text=t("btn_broadcast", lang), callback_data=MenuCB(section="broadcast").pack()))
    builder.row(InlineKeyboardButton(text=t("btn_help", lang), callback_data=MenuCB(section="help").pack()))
    return builder.as_markup()


def connect_account_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=t("btn_add_account", lang),
        callback_data=AccountCB(action="add").pack(),
    ))
    return builder.as_markup()


def accounts_list_kb(accounts: list[Account], lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        icon = t("account_active", lang) if acc.is_active else t("account_paused", lang)
        name = acc.tg_first_name or acc.tg_username or ""
        label = f"{icon} {name} {acc.phone}".strip()
        builder.row(
            InlineKeyboardButton(
                text=label[:32],
                callback_data=AccountCB(action="view", account_id=acc.id).pack(),
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=AccountCB(action="delete_confirm", account_id=acc.id).pack(),
            ),
        )
    builder.row(InlineKeyboardButton(text=t("btn_add_account", lang), callback_data=AccountCB(action="add").pack()))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def account_detail_kb(account_id: int, is_active: bool, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_text = "⏸ Pauza" if is_active else "▶️ Faollashtirish"
    builder.row(InlineKeyboardButton(text=toggle_text, callback_data=AccountCB(action="toggle", account_id=account_id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_delete_account", lang), callback_data=AccountCB(action="delete_confirm", account_id=account_id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="accounts").pack()))
    return builder.as_markup()


def delete_confirm_kb(account_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_confirm_delete", lang), callback_data=AccountCB(action="delete", account_id=account_id).pack()),
        InlineKeyboardButton(text=t("btn_no", lang), callback_data=AccountCB(action="view", account_id=account_id).pack()),
    )
    return builder.as_markup()


PAGE_SIZE = 8


def groups_list_kb(
    groups: list[Group],
    account_id: int,
    page: int = 0,
    lang: str = "uz",
) -> tuple[str, InlineKeyboardMarkup]:
    total_pages = max(1, (len(groups) + PAGE_SIZE - 1) // PAGE_SIZE)
    page_groups = groups[page * PAGE_SIZE: (page + 1) * PAGE_SIZE]

    builder = InlineKeyboardBuilder()
    for grp in page_groups:
        icon = t("group_active", lang) if grp.is_active else t("group_inactive", lang)
        title = grp.title[:24]
        builder.row(
            InlineKeyboardButton(
                text=f"{icon} {title}",
                callback_data=GroupCB(action="noop", group_id=grp.id, account_id=account_id, page=page).pack(),
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=GroupCB(action="delete_confirm", group_id=grp.id, account_id=account_id, page=page).pack(),
            ),
        )

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("btn_prev", lang), callback_data=GroupCB(action="list", account_id=account_id, page=page - 1).pack()))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("btn_next", lang), callback_data=GroupCB(action="list", account_id=account_id, page=page + 1).pack()))
    if nav:
        builder.row(*nav)

    builder.row(InlineKeyboardButton(text=t("btn_add_group", lang), callback_data=GroupCB(action="add", account_id=account_id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))

    header = t("groups_list", lang, count=len(groups), page=page + 1, total=total_pages)
    return header, builder.as_markup()


def group_delete_confirm_kb(group_id: int, account_id: int, page: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_confirm_delete", lang), callback_data=GroupCB(action="delete", group_id=group_id, account_id=account_id, page=page).pack()),
        InlineKeyboardButton(text=t("btn_no", lang), callback_data=GroupCB(action="list", account_id=account_id, page=page).pack()),
    )
    return builder.as_markup()


def select_account_kb(accounts: list[Account], context: str, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        name = acc.tg_first_name or acc.tg_username or acc.phone
        icon = t("account_active", lang) if acc.is_active else t("account_paused", lang)
        if context == "groups":
            builder.row(InlineKeyboardButton(
                text=f"{icon} {name}",
                callback_data=GroupCB(action="list", account_id=acc.id).pack(),
            ))
        else:
            builder.row(InlineKeyboardButton(
                text=f"{icon} {name}",
                callback_data=BroadcastCB(action="select_account", account_id=acc.id).pack(),
            ))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


INTERVALS = [1, 2, 3, 5, 15, 30, 60]


def interval_kb(account_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for m in INTERVALS:
        row.append(InlineKeyboardButton(
            text=f"{m} daq" if m < 60 else "1 soat",
            callback_data=BroadcastCB(action="set_interval", minutes=m, account_id=account_id).pack(),
        ))
        if len(row) == 4:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def broadcast_confirm_kb(account_id: int, minutes: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=t("btn_start_broadcast", lang),
        callback_data=BroadcastCB(action="start", account_id=account_id, minutes=minutes).pack(),
    ))
    builder.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def campaign_controls_kb(campaign: Campaign, groups_count: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if campaign.status == "running":
        builder.row(InlineKeyboardButton(text=t("btn_pause", lang), callback_data=BroadcastCB(action="pause", campaign_id=campaign.id).pack()))
    else:
        builder.row(InlineKeyboardButton(text=t("btn_resume", lang), callback_data=BroadcastCB(action="resume", campaign_id=campaign.id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_stats", lang), callback_data=BroadcastCB(action="stats", campaign_id=campaign.id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_stop", lang), callback_data=BroadcastCB(action="stop_confirm", campaign_id=campaign.id).pack()))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def stop_confirm_kb(campaign_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_confirm_delete", lang), callback_data=BroadcastCB(action="stop", campaign_id=campaign_id).pack()),
        InlineKeyboardButton(text=t("btn_no", lang), callback_data=BroadcastCB(action="stats", campaign_id=campaign_id).pack()),
    )
    return builder.as_markup()


def broadcast_menu_kb(active_count: int, account_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=t("btn_new_message", lang),
        callback_data=BroadcastCB(action="new_message", account_id=account_id).pack(),
    ))
    if active_count > 0:
        builder.row(InlineKeyboardButton(
            text=t("btn_active_messages", lang, count=active_count),
            callback_data=BroadcastCB(action="active_list", account_id=account_id).pack(),
        ))
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def campaigns_list_kb(
    campaigns: list[Campaign],
    account_id: int,
    lang: str = "uz",
) -> tuple[str, InlineKeyboardMarkup]:
    builder = InlineKeyboardBuilder()
    for i, camp in enumerate(campaigns):
        builder.row(InlineKeyboardButton(
            text=f"{i + 1}-habar 🟢",
            callback_data=BroadcastCB(action="detail", campaign_id=camp.id, account_id=account_id).pack(),
        ))
    builder.row(InlineKeyboardButton(
        text=t("btn_back", lang),
        callback_data=BroadcastCB(action="menu", account_id=account_id).pack(),
    ))
    header = t("campaigns_list", lang, count=len(campaigns))
    return header, builder.as_markup()


def campaign_detail_kb(campaign_id: int, account_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=t("btn_delete_campaign", lang),
        callback_data=BroadcastCB(action="delete_confirm", campaign_id=campaign_id, account_id=account_id).pack(),
    ))
    builder.row(InlineKeyboardButton(
        text=t("btn_back", lang),
        callback_data=BroadcastCB(action="active_list", account_id=account_id).pack(),
    ))
    return builder.as_markup()


def reminder_kb(campaign_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("reminder_yes", lang),
            callback_data=ReminderCB(action="yes", campaign_id=campaign_id).pack(),
        ),
        InlineKeyboardButton(
            text=t("reminder_no", lang),
            callback_data=ReminderCB(action="no", campaign_id=campaign_id).pack(),
        ),
    )
    return builder.as_markup()


def settings_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data=SettingsCB(action="lang_uz").pack()),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data=SettingsCB(action="lang_ru").pack()),
    )
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def back_to_main_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("btn_back", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()


def cancel_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("btn_cancel", lang), callback_data=MenuCB(section="main").pack()))
    return builder.as_markup()
