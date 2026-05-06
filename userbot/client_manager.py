import asyncio
from loguru import logger
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from utils.crypto import decrypt


class ClientManager:
    """
    Manages multiple Telethon clients:
    - Permanent clients: keyed by account_id
    - Temporary clients: keyed by "temp_{user_tg_id}" during login flow
    """

    def __init__(self) -> None:
        self._clients: dict[int, TelegramClient] = {}
        self._temp: dict[str, TelegramClient] = {}

    # ── Permanent clients ─────────────────────────────────────────────────────

    async def get_client(self, account_id: int, session_encrypted: str) -> TelegramClient:
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
        logger.debug(f"Temp client created for user {user_id}")
        return client

    async def promote_temp_client(self, user_id: int, account_id: int) -> str:
        """Move temp client to permanent pool, return saved session string."""
        key = self._temp_key(user_id)
        client = self._temp.pop(key, None)
        if not client:
            raise RuntimeError("No temp client found for user")
        session_str = client.session.save()
        self._clients[account_id] = client
        return session_str

    async def remove_temp_client(self, user_id: int) -> None:
        key = self._temp_key(user_id)
        client = self._temp.pop(key, None)
        if client and client.is_connected():
            await client.disconnect()

    async def disconnect_all(self) -> None:
        for client in list(self._clients.values()) + list(self._temp.values()):
            if client.is_connected():
                await client.disconnect()
        self._clients.clear()
        self._temp.clear()


# Global singleton
client_manager = ClientManager()
