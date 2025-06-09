from aiogram import Router, types
from aiogram.filters.command import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select

from core.database import AsyncSessionLocal
from core.models import Event

router = Router()


@router.message(lambda message: message.text and "Удалить мероприятие" in message.text)
async def delete_event_start(
    message: types.Message, command: CommandObject | None = None
):
    """Показывает список мероприятий для удаления"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()

    if not events:
        await message.answer("❌ Нет мероприятий для удаления.")
        return

    kb = InlineKeyboardBuilder()
    for event in events:
        kb.button(text=event.title, callback_data=f"delete_event_{event.id}")

    kb.adjust(1)
    await message.answer(
        "❌ Выберите мероприятие для удаления:", reply_markup=kb.as_markup()
    )


@router.callback_query(lambda c: c.data.startswith("delete_event_"))
async def delete_event(
    callback: types.CallbackQuery, command: CommandObject | None = None
):
    """Удаляет выбранное мероприятие"""
    event_id = int(callback.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event).where(Event.id == event_id))
        event = result.scalars().first()

        if event:
            await session.delete(event)
            await session.commit()
            await callback.message.answer(f"✅ Мероприятие {event.title} удалено!")
        else:
            await callback.message.answer("❌ Ошибка! Мероприятие не найдено.")

    await callback.answer()
