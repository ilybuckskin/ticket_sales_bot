from aiogram import Router, types
from aiogram.filters.command import CommandObject
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import User

router = Router()


@router.message(lambda message: message.text and "Список пользователей" in message.text)
async def list_users(message: types.Message, command: CommandObject | None = None):
    """Отображает список пользователей"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

    if not users:
        await message.answer("❌ Нет зарегистрированных пользователей.")
        return

    response = "📋 Список пользователей:\n"
    for user in users:
        response += f"\n👤 {user.username or 'Без имени'} (ID: {user.telegram_id})"

    await message.answer(response)
