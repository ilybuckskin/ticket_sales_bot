from aiogram import Router, types
from sqlalchemy.future import select

from bot.keyboards.admin import admin_menu
from bot.keyboards.manager import manager_menu
from core.database import AsyncSessionLocal
from core.models import User

router = Router()


@router.message(lambda message: message.text and "Назад" in message.text)
async def universal_back(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalars().first()

    if user and user.is_admin:
        await message.answer("🔙 Возврат в админ-панель.", reply_markup=admin_menu())
    elif user and user.is_manager:
        await message.answer(
            "🔙 Возврат в меню менеджера.", reply_markup=manager_menu()
        )
    else:
        await message.answer("⚠️ У вас нет доступа ни к одному из меню.")
