import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from aiogram import Router, types
from aiogram.filters.command import CommandObject
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal
from core.models import Ticket, User

router = Router()


@router.message(lambda message: message.text and "Мои билеты" in message.text)
async def my_tickets(message: types.Message, command: CommandObject | None = None):
    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            await message.answer("❗ Вы еще не зарегистрированы в системе.")
            return

        result = await session.execute(
            select(Ticket)
            .options(selectinload(Ticket.event))
            .where(Ticket.user_id == user.id)
        )
        tickets = result.scalars().all()

    if not tickets:
        await message.answer("📭 У вас пока нет купленных билетов.")
        return

    response = "🎟 Ваши билеты:\n"
    for ticket in tickets:
        event = ticket.event
        response += f"\n📍 <b>{event.title}</b>\n🗓 {event.date.strftime('%d.%m.%Y %H:%M')}\n🎫 ID: {ticket.id}\n"

    await message.answer(response, parse_mode="HTML")
