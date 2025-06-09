from datetime import datetime

from aiogram import Bot, Router, types
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.admin import event_menu
from core.database import AsyncSessionLocal
from core.models import Event

router = Router()


class AddEvent(StatesGroup):
    title = State()
    description = State()
    date = State()
    total_tickets = State()
    cover = State()


@router.message(lambda message: message.text and "Добавить мероприятие" in message.text)
async def add_event_start(
    message: types.Message, state: FSMContext, command: CommandObject | None = None
):
    """Начинаем процесс добавления мероприятия"""
    await state.set_state(AddEvent.title)
    await message.answer("📝 Введите название мероприятия:")


@router.message(AddEvent.title)
async def add_event_title(
    message: types.Message, state: FSMContext, command: CommandObject | None = None
):
    """Сохраняем название мероприятия"""
    await state.update_data(title=message.text)
    await state.set_state(AddEvent.description)
    await message.answer("📄 Введите описание мероприятия:")


@router.message(AddEvent.description)
async def add_event_description(
    message: types.Message, state: FSMContext, command: CommandObject | None = None
):
    """Сохраняем описание мероприятия"""
    await state.update_data(description=message.text)
    await state.set_state(AddEvent.date)
    await message.answer("📆 Введите дату мероприятия (гггг-мм-дд чч:мм):")


@router.message(AddEvent.date)
async def add_event_date(message: types.Message, state: FSMContext):
    """Сохраняем дату мероприятия (конвертируем в datetime)"""
    try:
        parsed_date = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(
            "❗ Неверный формат даты. Введите дату в формате: гггг-мм-дд чч:мм\nПример: 2025-04-27 19:30"
        )
        return

    await state.update_data(date=parsed_date)
    await state.set_state(AddEvent.total_tickets)
    await message.answer("🎟 Введите количество билетов:")


@router.message(AddEvent.total_tickets)
async def add_event_total_tickets(message: types.Message, state: FSMContext):
    """Запросить обложку после билетов"""
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("❗ Введите корректное количество билетов:")
        return

    await state.update_data(total_tickets=int(message.text))
    await state.set_state(AddEvent.cover)
    await message.answer(
        "📸 Пришлите обложку мероприятия (фото в ответ на это сообщение):"
    )


from pathlib import Path


@router.message(AddEvent.cover)
async def add_event_cover(message: types.Message, state: FSMContext, bot: Bot):
    """Сохраняем обложку мероприятия"""
    if not message.photo:
        await message.answer("❗ Пожалуйста, отправьте именно фото.")
        return

    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        # создаём событие без обложки
        event = Event(
            title=data["title"],
            description=data["description"],
            date=data["date"],
            total_tickets=data["total_tickets"],
            sold_tickets=0,
        )
        session.add(event)
        await session.flush()

        # создаем путь
        event_dir = Path("media/events")
        event_dir.mkdir(parents=True, exist_ok=True)
        cover_path = event_dir / f"{event.id}.jpg"

        photo: types.PhotoSize = message.photo[-1]

        # скачиваем файл по file_id
        await bot.download(file=photo.file_id, destination=cover_path)

        event.cover_path = str(cover_path)
        await session.commit()

    await state.clear()
    await message.answer(
        "✅ Мероприятие создано вместе с обложкой!", reply_markup=event_menu()
    )
