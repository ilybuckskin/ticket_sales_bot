import re

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select

from bot.keyboards.main import main_menu
from bot.utils.pdf_ticket import generate_ticket_pdf
from core.database import AsyncSessionLocal
from core.models import Event, Ticket, User

router = Router()


class BuyTicket(StatesGroup):
    event_id = State()
    quantity = State()
    full_name = State()
    phone = State()
    email = State()
    waiting_for_payment = State()


@router.callback_query(lambda c: c.data.startswith("event_"))
async def choose_event(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    await state.update_data(event_id=event_id)
    await state.set_state(BuyTicket.quantity)
    await callback.message.answer("Введите количество билетов:")
    await callback.answer()


@router.message(BuyTicket.quantity)
async def input_quantity(message: types.Message, state: FSMContext):
    """Проверяем количество билетов"""
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer(
            "❗ Введите корректное количество билетов (число больше 0):"
        )
        return

    quantity = int(message.text)

    data = await state.get_data()
    event_id = data.get("event_id")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event).where(Event.id == event_id))
        event = result.scalars().first()

        if not event:
            await message.answer("❗ Ошибка! Мероприятие не найдено.")
            await state.clear()
            return

        available_tickets = event.total_tickets - event.sold_tickets

        if quantity > available_tickets:
            await message.answer(
                f"❗ Недостаточно билетов. Доступно только {available_tickets} шт. Введите другое количество:"
            )
            return

    await state.update_data(quantity=quantity)
    await state.set_state(BuyTicket.full_name)
    await message.answer("Введите ваше ФИО:")


@router.message(BuyTicket.full_name)
async def input_full_name(message: types.Message, state: FSMContext):
    """Запрашиваем телефон"""
    if len(message.text.strip()) < 3:
        await message.answer("❗ ФИО слишком короткое. Введите полное имя:")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(BuyTicket.phone)
    await message.answer(
        "Введите номер телефона (только цифры, например 994501112233):"
    )


@router.message(BuyTicket.phone)
async def input_phone(message: types.Message, state: FSMContext):
    """Валидация телефона"""
    phone = message.text.strip()

    if not phone.isdigit() or len(phone) < 10:
        await message.answer(
            "❗ Некорректный номер телефона. Введите только цифры, минимум 10 символов:"
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(BuyTicket.email)
    await message.answer("Введите ваш Email:")


@router.message(BuyTicket.email)
async def input_email(message: types.Message, state: FSMContext):
    """Запросить оплату"""

    email = message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await message.answer("❗ Некорректный Email. Попробуйте снова:")
        return

    await state.update_data(email=email)
    await state.set_state(BuyTicket.waiting_for_payment)

    # TODO: Добавить платежный сервис
    await message.answer(
        "💳 Для завершения покупки перейдите по ссылке для оплаты:\n\n"
        "👉 https://example.com/pay (тестовый платеж)\n\n"
        "Когда оплатите — нажмите кнопку ниже:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="✅ Я оплатил")]], resize_keyboard=True
        ),
    )


@router.message(lambda message: message.text == "✅ Я оплатил")
async def confirm_payment(message: types.Message, state: FSMContext):
    """Подтверждение тестовой оплаты и выдача билетов"""
    data = await state.get_data()
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.id == data["event_id"])
        )
        event = result.scalars().first()

        user_result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = user_result.scalars().first()

        if not user:
            user = User(telegram_id=user_id, username=message.from_user.username)
            session.add(user)
            await session.flush()

        tickets = []
        for _ in range(data["quantity"]):
            ticket = Ticket(user_id=user.id, event_id=data["event_id"], is_used=False)
            session.add(ticket)
            await session.flush()
            tickets.append(ticket)

        event.sold_tickets += len(tickets)
        await session.commit()

    await state.clear()

    # Отправляем билеты
    for ticket in tickets:
        pdf_buffer = generate_ticket_pdf(
            event_title=event.title,
            event_date=event.date,
            ticket_id=ticket.id,
            background_path=event.cover_path,
        )

        await message.answer_document(
            types.BufferedInputFile(
                pdf_buffer.read(), filename=f"ticket_{ticket.id}.pdf"
            )
        )

    await message.answer(
        "✅ Оплата успешно подтверждена и билеты высланы!", reply_markup=main_menu()
    )
