import asyncio
import time

from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from utils.crypto import decrypt


IDLE_DISCONNECT_SECONDS = 300  # 5 minutes
SWEEP_INTERVAL_SECONDS = 60


class ClientManager:
    """
    Manages multiple Telethon clients:
    - Permanent clients: keyed by account_id, idle-disconnected after 5 min
    - Temporary clients: keyed by "temp_{user_tg_id}" during login flow
    """

    def __init__(self) -> None:
        self._clients: dict[int, TelegramClient] = {}
        self._last_used: dict[int, float] = {}
        self._temp: dict[str, TelegramClient] = {}
        self._sweep_task: asyncio.Task | None = None

    def start_idle_sweeper(self) -> None:
        if self._sweep_task is None or self._sweep_task.done():
            self._sweep_task = asyncio.create_task(self._sweep_loop())

    async def _sweep_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(SWEEP_INTERVAL_SECONDS)
                now = time.time()
                stale = [
                    aid for aid, ts in self._last_used.items()
                    if now - ts > IDLE_DISCONNECT_SECONDS
                ]
                for aid in stale:
                    client = self._clients.pop(aid, None)
                    self._last_used.pop(aid, None)
                    if client and client.is_connected():
                        try:
                            await client.disconnect()
                        except Exception:
                            pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"idle sweeper error: {e}")

    # ── Permanent clients ─────────────────────────────────────────────────────

    async def get_client(self, account_id: int, session_encrypted: str) -> TelegramClient:
        self._last_used[account_id] = time.time()
        if account_id in self._clients:
            client = self._clients[account_id]
            if not client.is_connected():
                await client.connect()
            return client

        session_str = decrypt(session_encrypted)
        client = TelegramClient(StringSession(session_str), settings.api_id, settings.api_hash)
        await client.connect()
        self._clients[account_id] = client
        return client

    async def remove_client(self, account_id: int) -> None:
        client = self._clients.pop(account_id, None)
        self._last_used.pop(account_id, None)
        if client and client.is_connected():
            await client.disconnect()

    # ── Temporary clients (auth flow) ─────────────────────────────────────────

    def _temp_key(self, user_id: int) -> str:
        return f"temp_{user_id}"

    async def get_temp_client(self, user_id: int) -> TelegramClient:
        key = self._temp_key(user_id)
        if key in self._temp:
            client = self._temp[key]
            if not client.is_connected():
                await client.connect()
            return client

        client = TelegramClient(StringSession(), settings.api_id, settings.api_hash)
        await client.connect()
        self._temp[key] = client
        return client

    async def promote_temp_client(self, user_id: int, account_id: int) -> str:
        """Move temp client to permanent pool, return saved session string."""
        key = self._temp_key(user_id)
        client = self._temp.pop(key, None)
        if not client:
            raise RuntimeError("No temp client found for user")
        session_str = client.session.save()
        self._clients[account_id] = client
        self._last_used[account_id] = time.time()
        return session_str

    async def remove_temp_client(self, user_id: int) -> None:
        key = self._temp_key(user_id)
        client = self._temp.pop(key, None)
        if client and client.is_connected():
            await client.disconnect()

    async def disconnect_all(self) -> None:
        if self._sweep_task and not self._sweep_task.done():
            self._sweep_task.cancel()
        for client in list(self._clients.values()) + list(self._temp.values()):
            if client.is_connected():
                try:
                    await client.disconnect()
                except Exception:
                    pass
        self._clients.clear()
        self._last_used.clear()
        self._temp.clear()


# Global singleton
client_manager = ClientManager()
