from aiogram import Router
from aiogram.types import Message
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import User

router = Router()

MANAGER_MESSAGE = (
    "Пользователь @{username} ({telegram_id}) просит связаться. Напишите ему напрямую."
)


@router.message(
    lambda message: message.text and "Связаться с менеджером" in message.text
)
async def contact_manager(message: Message):
    async with AsyncSessionLocal() as session:
        managers = await session.execute(select(User).where(User.is_manager == True))
        managers = managers.scalars().all()

        if not managers:
            await message.answer("Менеджеры пока недоступны.")
            return

        for manager in managers:
            try:
                await message.bot.send_message(
                    chat_id=manager.telegram_id,
                    text=MANAGER_MESSAGE.format(
                        username=message.from_user.username or "без username",
                        telegram_id=message.from_user.id,
                    ),
                )
            except Exception:
                pass

        await message.answer("Мы уведомили менеджера. Он свяжется с вами в Telegram.")
