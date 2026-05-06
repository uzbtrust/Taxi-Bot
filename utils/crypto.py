from cryptography.fernet import Fernet
from config import settings

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.fernet_key
        if isinstance(key, str):
            key = key.encode()
        _fernet = Fernet(key)
    return _fernet


def encrypt(text: str) -> str:
    return _get_fernet().encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return _get_fernet().decrypt(token.encode()).decode()
