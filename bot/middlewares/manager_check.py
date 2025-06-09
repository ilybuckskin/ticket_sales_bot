from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.models import User


class ManagerMiddleware(BaseMiddleware):
    """Middleware для проверки менеджеров"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == event.from_user.id)
            )
            user = result.scalars().first()

            if user and user.is_manager:
                return await handler(event, data)

        await event.answer("⛔ У вас нет доступа к панели менеджера.")
