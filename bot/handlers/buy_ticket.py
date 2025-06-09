import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from aiogram import Router, types
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import Event

router = Router()


@router.message(lambda message: message.text and "Купить билет" in message.text)
async def buy_ticket(message: types.Message, command: CommandObject | None = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()

    if not events:
        await message.answer("Сейчас нет доступных мероприятий.")
        return

    kb = InlineKeyboardBuilder()
    for event in events:
        kb.button(text=event.title, callback_data=f"event_{event.id}")

    kb.adjust(1)

    await message.answer("Выберите мероприятие:", reply_markup=kb.as_markup())
