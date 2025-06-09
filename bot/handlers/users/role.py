from aiogram import Router, types
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import User

router = Router()


@router.message(lambda message: message.text and "Назначить менеджера" in message.text)
async def assign_manager_start(
    message: types.Message, command: CommandObject | None = None
):
    """Выводит список пользователей для назначения менеджером"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.is_manager == False))
        users = result.scalars().all()

    if not users:
        await message.answer("❌ Нет пользователей для назначения менеджером.")
        return

    kb = InlineKeyboardBuilder()
    for user in users:
        kb.button(
            text=user.username or f"ID: {user.telegram_id}",
            callback_data=f"make_manager_{user.telegram_id}",
        )

    kb.adjust(1)
    await message.answer(
        "🔹 Выберите пользователя для назначения менеджером:",
        reply_markup=kb.as_markup(),
    )


@router.callback_query(lambda c: c.data.startswith("make_manager_"))
async def assign_manager(
    callback: types.CallbackQuery, command: CommandObject | None = None
):
    """Назначает пользователя менеджером"""
    user_id = int(callback.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalars().first()

        if user:
            user.is_manager = True
            await session.commit()
            await callback.message.answer(
                f"✅ Пользователь {user.username or user_id} теперь менеджер!"
            )
        else:
            await callback.message.answer("❌ Ошибка! Пользователь не найден.")

    await callback.answer()
