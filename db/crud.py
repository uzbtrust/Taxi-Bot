from datetime import datetime, timedelta
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Account, Campaign, Group, SendLog, User


# ── User ──────────────────────────────────────────────────────────────────────

async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == tg_id))
    return result.scalar_one_or_none()


async def get_or_create_user(
    session: AsyncSession,
    tg_id: int,
    username: str | None,
    first_name: str | None,
) -> tuple[User, bool]:
    user = await get_user(session, tg_id)
    if user:
        return user, False
    user = User(id=tg_id, username=username, first_name=first_name)
    session.add(user)
    await session.commit()
    return user, True


async def set_language(session: AsyncSession, tg_id: int, lang: str) -> None:
    user = await get_user(session, tg_id)
    if user:
        user.language = lang
        await session.commit()


# ── Account ───────────────────────────────────────────────────────────────────

async def get_accounts(session: AsyncSession, user_id: int) -> list[Account]:
    result = await session.execute(
        select(Account).where(Account.user_id == user_id).order_by(Account.created_at)
    )
    return list(result.scalars().all())


async def get_account(session: AsyncSession, account_id: int) -> Account | None:
    result = await session.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()


async def create_account(
    session: AsyncSession,
    user_id: int,
    phone: str,
    tg_account_id: int,
    tg_username: str | None,
    tg_first_name: str | None,
    session_encrypted: str,
) -> Account:
    acc = Account(
        user_id=user_id,
        phone=phone,
        tg_account_id=tg_account_id,
        tg_username=tg_username,
        tg_first_name=tg_first_name,
        session_encrypted=session_encrypted,
    )
    session.add(acc)
    await session.commit()
    await session.refresh(acc)
    return acc


async def toggle_account(session: AsyncSession, account_id: int) -> bool:
    acc = await get_account(session, account_id)
    if acc:
        acc.is_active = not acc.is_active
        await session.commit()
        return acc.is_active
    return False


async def delete_account(session: AsyncSession, account_id: int) -> None:
    acc = await get_account(session, account_id)
    if acc:
        await session.delete(acc)
        await session.commit()


async def update_session(session: AsyncSession, account_id: int, session_encrypted: str) -> None:
    acc = await get_account(session, account_id)
    if acc:
        acc.session_encrypted = session_encrypted
        await session.commit()


# ── Group ─────────────────────────────────────────────────────────────────────

async def get_groups(session: AsyncSession, account_id: int) -> list[Group]:
    result = await session.execute(
        select(Group).where(Group.account_id == account_id).order_by(Group.added_at)
    )
    return list(result.scalars().all())


async def get_active_groups(session: AsyncSession, account_id: int) -> list[Group]:
    result = await session.execute(
        select(Group)
        .where(Group.account_id == account_id, Group.is_active == True)
        .order_by(Group.added_at)
    )
    return list(result.scalars().all())


async def get_group(session: AsyncSession, group_id: int) -> Group | None:
    result = await session.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()


async def group_exists(session: AsyncSession, account_id: int, chat_id: int) -> bool:
    result = await session.execute(
        select(Group).where(Group.account_id == account_id, Group.chat_id == chat_id)
    )
    return result.scalar_one_or_none() is not None


async def create_group(
    session: AsyncSession,
    account_id: int,
    chat_id: int,
    title: str,
    username: str | None = None,
    invite_link: str | None = None,
) -> Group:
    grp = Group(
        account_id=account_id,
        chat_id=chat_id,
        title=title,
        username=username,
        invite_link=invite_link,
    )
    session.add(grp)
    await session.commit()
    await session.refresh(grp)
    return grp


async def toggle_group(session: AsyncSession, group_id: int) -> bool:
    grp = await get_group(session, group_id)
    if grp:
        grp.is_active = not grp.is_active
        await session.commit()
        return grp.is_active
    return False


async def delete_group(session: AsyncSession, group_id: int) -> None:
    grp = await get_group(session, group_id)
    if grp:
        await session.delete(grp)
        await session.commit()


async def disable_group(session: AsyncSession, group_id: int) -> None:
    grp = await get_group(session, group_id)
    if grp:
        grp.is_active = False
        await session.commit()


# ── Campaign ──────────────────────────────────────────────────────────────────

async def get_campaign(session: AsyncSession, campaign_id: int) -> Campaign | None:
    result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalar_one_or_none()


async def get_campaigns_by_account(session: AsyncSession, account_id: int) -> list[Campaign]:
    """All running/paused campaigns for a given account."""
    result = await session.execute(
        select(Campaign)
        .where(
            Campaign.account_id == account_id,
            Campaign.status.in_(["running", "paused"]),
        )
        .order_by(Campaign.created_at)
    )
    return list(result.scalars().all())


async def get_all_running_campaigns(session: AsyncSession) -> list[Campaign]:
    result = await session.execute(
        select(Campaign)
        .options(selectinload(Campaign.account))
        .where(Campaign.status == "running")
    )
    return list(result.scalars().all())


async def create_campaign(
    session: AsyncSession,
    account_id: int,
    user_tg_id: int,
    message_text: str,
    interval_minutes: int,
) -> Campaign:
    camp = Campaign(
        account_id=account_id,
        user_tg_id=user_tg_id,
        message_text=message_text,
        interval_minutes=interval_minutes,
    )
    session.add(camp)
    await session.commit()
    await session.refresh(camp)
    return camp


async def set_campaign_status(session: AsyncSession, campaign_id: int, status: str) -> None:
    camp = await get_campaign(session, campaign_id)
    if camp:
        camp.status = status
        if status == "stopped":
            camp.stopped_at = datetime.utcnow()
        await session.commit()


async def delete_campaign(session: AsyncSession, campaign_id: int) -> None:
    camp = await get_campaign(session, campaign_id)
    if camp:
        await session.delete(camp)
        await session.commit()


async def increment_campaign_sent(session: AsyncSession, campaign_id: int, count: int) -> None:
    camp = await get_campaign(session, campaign_id)
    if camp:
        camp.total_sent += count
        await session.commit()


async def increment_campaign_failed(session: AsyncSession, campaign_id: int, count: int) -> None:
    camp = await get_campaign(session, campaign_id)
    if camp:
        camp.total_failed += count
        await session.commit()


# ── SendLog ───────────────────────────────────────────────────────────────────

async def create_send_log(
    session: AsyncSession,
    campaign_id: int,
    group_id: int | None,
    group_title: str | None,
    status: str,
    error: str | None = None,
) -> SendLog:
    log = SendLog(
        campaign_id=campaign_id,
        group_id=group_id,
        group_title=group_title,
        status=status,
        error=error,
    )
    session.add(log)
    await session.commit()
    return log


# ── Admin stats ───────────────────────────────────────────────────────────────

async def get_admin_stats(session: AsyncSession) -> dict:
    total_users = (await session.execute(func.count(User.id).select())).scalar() or 0
    total_accounts = (await session.execute(func.count(Account.id).select())).scalar() or 0
    total_groups = (await session.execute(func.count(Group.id).select())).scalar() or 0
    total_campaigns = (await session.execute(func.count(Campaign.id).select())).scalar() or 0
    active_campaigns = (
        await session.execute(
            select(func.count(Campaign.id)).where(Campaign.status == "running")
        )
    ).scalar() or 0
    total_sent = (await session.execute(select(func.sum(Campaign.total_sent)))).scalar() or 0

    # Messages per day last 7 days
    days_data: list[dict] = []
    for i in range(6, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = (
            await session.execute(
                select(func.count(SendLog.id)).where(
                    SendLog.sent_at >= day_start,
                    SendLog.sent_at < day_end,
                    SendLog.status == "ok",
                )
            )
        ).scalar() or 0
        days_data.append({"date": day_start.strftime("%d/%m"), "count": count})

    # Users per day last 7 days
    users_data: list[dict] = []
    for i in range(6, -1, -1):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = (
            await session.execute(
                select(func.count(User.id)).where(
                    User.created_at >= day_start,
                    User.created_at < day_end,
                )
            )
        ).scalar() or 0
        users_data.append({"date": day_start.strftime("%d/%m"), "count": count})

    # Campaign status breakdown
    status_rows = (
        await session.execute(
            select(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status)
        )
    ).all()
    status_counts = {row[0]: row[1] for row in status_rows}

    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "total_groups": total_groups,
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_sent": total_sent,
        "days_data": days_data,
        "users_data": users_data,
        "status_counts": status_counts,
    }
