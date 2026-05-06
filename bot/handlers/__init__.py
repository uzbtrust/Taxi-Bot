from bot.handlers.admin import router as admin_router
from bot.handlers.start import router as start_router
from bot.handlers.auth import router as auth_router
from bot.handlers.menu import router as menu_router
from bot.handlers.accounts import router as accounts_router
from bot.handlers.groups import router as groups_router
from bot.handlers.broadcast import router as broadcast_router

__all__ = [
    "admin_router",
    "start_router",
    "auth_router",
    "menu_router",
    "accounts_router",
    "groups_router",
    "broadcast_router",
]
