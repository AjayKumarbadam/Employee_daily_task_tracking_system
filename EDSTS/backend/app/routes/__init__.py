from .auth import router as auth_router
from .users import router as users_router
from .tasks import router as tasks_router
from .daily_updates import router as daily_updates_router
from .dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "users_router",
    "tasks_router",
    "daily_updates_router",
    "dashboard_router",
]
