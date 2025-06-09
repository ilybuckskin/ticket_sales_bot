import asyncio
import logging
import pathlib
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.admin import router as admin_router
from bot.handlers.broadcast import router as broadcast_router
from bot.handlers.buy import router as buy_router
from bot.handlers.buy_ticket import router as buy_ticket_router
from bot.handlers.common import router as common_router
from bot.handlers.events import router as events_router
from bot.handlers.help import router as help_router
from bot.handlers.my_tickets import router as my_tickets_router
from bot.handlers.scan_ticket import router as scan_ticket_router
from bot.handlers.users import router as users_router
from bot.keyboards.main import main_menu
from core.config import settings
from core.database import AsyncSessionLocal
from core.models import User

sys.path.append(str(pathlib.Path(__file__).parent.parent))


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),  # Указываем parse_mode здесь
)
dp = Dispatcher()

dp.include_router(buy_ticket_router)
dp.include_router(my_tickets_router)
dp.include_router(admin_router)
dp.include_router(events_router)
dp.include_router(users_router)
dp.include_router(buy_router)
dp.include_router(help_router)
dp.include_router(scan_ticket_router)
dp.include_router(broadcast_router)
dp.include_router(common_router)


# Функция для регистрации пользователя
async def register_user(session: AsyncSession, telegram_id: int, username: str):
    user = await session.get(User, telegram_id)
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalars().first()

        if not user:
            user = User(
                telegram_id=message.from_user.id, username=message.from_user.username
            )
            session.add(user)
            await session.commit()

    await message.answer(
        "Привет! Добро пожаловать в билетного бота 🎟\nВыберите действие ниже:",
        reply_markup=main_menu(),
    )


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
