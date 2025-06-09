import pathlib
import sys

from aiogram.fsm.context import FSMContext

from bot.keyboards.manager import manager_menu
from bot.middlewares.manager_check import ManagerMiddleware

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from io import BytesIO

from aiogram import F, Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from PIL import Image
from pyzbar.pyzbar import decode
from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.models import Event, Ticket, User

router = Router()
router.message.middleware(ManagerMiddleware())


class ScanState(StatesGroup):
    event_selection = State()
    awaiting_photo = State()


@router.message(Command("manager"))
async def show_manager_menu(message: types.Message):
    await message.answer(
        "🛠 Меню менеджера. Выберите действие:",
        reply_markup=manager_menu(),
    )


@router.message(F.text == "📷 Сканировать билет")
async def prompt_scan_ticket(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()

    if not events:
        await message.answer("Нет доступных мероприятий для сканирования.")
        return

    kb = InlineKeyboardBuilder()
    for event in events:
        kb.button(text=event.title, callback_data=f"scan_event_{event.id}")
    kb.adjust(1)

    await state.set_state(ScanState.event_selection)
    await message.answer(
        "Выберите мероприятие для проверки билетов:", reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("scan_event_"), ScanState.event_selection)
async def select_event_for_scanning(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.replace("scan_event_", ""))
    await state.update_data(selected_event_id=event_id)
    await state.set_state(ScanState.awaiting_photo)
    await callback.message.answer("📸 Теперь отправьте фото с QR-кодом билета.")
    await callback.answer()


@router.callback_query(F.data == "cancel_scan", ScanState.event_selection)
async def cancel_scan(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalars().first()

    if user and user.is_manager:
        kb = manager_menu()
        text = "🔙 Возврат в меню менеджера."
    else:
        kb = types.ReplyKeyboardRemove()
        text = "🔙 Возврат."

    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@router.message(F.text == "🔙 Завершить сканирование", ScanState.awaiting_photo)
async def stop_scanning(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Вы завершили сканирование.", reply_markup=manager_menu())


@router.message(F.photo, ScanState.awaiting_photo)
async def process_ticket_scan(message: types.Message, state: FSMContext):
    data = await state.get_data()
    expected_event_id = data.get("selected_event_id")
    """Обработка фото QR-кода и проверка билета"""
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalars().first()

        if not user or not user.is_manager:
            await message.answer("⛔ У вас нет прав для сканирования билетов.")
            return

        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        content = await message.bot.download_file(file.file_path)

        try:
            image = Image.open(BytesIO(content.read()))
            qr_list = decode(image)
        except Exception:
            await message.answer("❌ Не удалось обработать изображение.")
            return

        if not qr_list:
            await message.answer("❗ QR-код не найден.")
            return

        data = qr_list[0].data.decode("utf-8")

        if not data.startswith("TICKET:"):
            await message.answer("⚠️ Неверный формат QR-кода.")
            return

        try:
            ticket_id = int(data.replace("TICKET:", ""))
        except ValueError:
            await message.answer("⚠️ Некорректный ID билета.")
            return

        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()

        if not ticket:
            await message.answer(f"❌ Билет #{ticket_id} не найден.")
            return

        if ticket.is_used:
            await message.answer(f"🚫 Билет #{ticket_id} уже использован.")
            return

        if ticket.event_id != expected_event_id:
            await message.answer("🚫 Билет не принадлежит выбранному мероприятию.")
            return

        ticket.is_used = True
        await session.commit()
        await state.clear()

        await message.answer(
            f"✅ Билет #{ticket_id} успешно верифицирован.\n"
            f"Отправьте следующий QR-код или нажмите 🔙 Завершить сканирование."
        )
