from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(8), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    phone: Mapped[str] = mapped_column(String(32))
    tg_account_id: Mapped[int | None] = mapped_column(BigInteger)
    tg_username: Mapped[str | None] = mapped_column(String(64))
    tg_first_name: Mapped[str | None] = mapped_column(String(128))
    session_encrypted: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="accounts")
    groups: Mapped[list["Group"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"))
    chat_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(String(256))
    username: Mapped[str | None] = mapped_column(String(64))
    invite_link: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    account: Mapped["Account"] = relationship(back_populates="groups")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"))
    user_tg_id: Mapped[int] = mapped_column(BigInteger)          # owner tg id
    message_text: Mapped[str] = mapped_column(Text)
    interval_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="running")  # running|paused|stopped
    total_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    account: Mapped["Account"] = relationship(back_populates="campaigns")
    logs: Mapped[list["SendLog"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class SendLog(Base):
    __tablename__ = "send_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id"))
    group_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    group_title: Mapped[str | None] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(16))   # ok | slowmode | flood | forbidden | error
    error: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    campaign: Mapped["Campaign"] = relationship(back_populates="logs")
