from aiogram import Router, types
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import User

router = Router()


@router.message(
    lambda message: message.text and "Заблокировать пользователя" in message.text
)
async def block_user_start(
    message: types.Message, command: CommandObject | None = None
):
    """Показывает список пользователей для блокировки"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.is_admin == False))
        users = result.scalars().all()

    if not users:
        await message.answer("❌ Нет пользователей для блокировки.")
        return

    kb = InlineKeyboardBuilder()
    for user in users:
        kb.button(
            text=user.username or f"ID: {user.telegram_id}",
            callback_data=f"block_{user.telegram_id}",
        )

    kb.adjust(1)
    await message.answer(
        "🚫 Выберите пользователя для блокировки:", reply_markup=kb.as_markup()
    )


@router.callback_query(lambda c: c.data.startswith("block_"))
async def block_user(
    callback: types.CallbackQuery, command: CommandObject | None = None
):
    """Блокирует пользователя"""
    user_id = int(callback.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalars().first()

        if user:
            user.is_blocked = True
            await session.commit()
            await callback.message.answer(
                f"✅ Пользователь {user.username or user_id} заблокирован!"
            )
        else:
            await callback.message.answer("❌ Ошибка! Пользователь не найден.")

    await callback.answer()
