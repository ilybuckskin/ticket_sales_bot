from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.future import select

from bot.middlewares.admin_check import AdminMiddleware
from core.database import AsyncSessionLocal
from core.models import User

router = Router()
router.message.middleware(AdminMiddleware())


class BroadcastState(StatesGroup):
    text = State()
    media = State()
    confirm = State()


@router.message(F.text == "📢 Рассылка")
async def start_broadcast(message: Message, state: FSMContext):
    await state.set_state(BroadcastState.text)
    await message.answer("✉️ Введите текст для рассылки:")


@router.message(BroadcastState.text)
async def receive_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(BroadcastState.media)
    await message.answer("📎 Пришлите фото/видео/файл (или /skip):")


@router.message(Command("skip"), BroadcastState.media)
async def skip_media(message: Message, state: FSMContext):
    await state.update_data(media=None)
    await state.set_state(BroadcastState.confirm)
    await message.answer("✅ Готово к отправке. Напишите /send для рассылки.")


@router.message(
    BroadcastState.media, F.content_type.in_({"photo", "video", "document"})
)
async def receive_media(message: Message, state: FSMContext):
    await state.update_data(media=message)
    await state.set_state(BroadcastState.confirm)
    await message.answer("✅ Медиа получено. Напишите /send для рассылки.")


@router.message(Command("send"), BroadcastState.confirm)
async def send_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    media_msg: Message = data.get("media")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = result.scalars().all()

    success, fail = 0, 0
    for uid in user_ids:
        try:
            if media_msg:
                if media_msg.photo:
                    await message.bot.send_photo(
                        uid, media_msg.photo[-1].file_id, caption=text
                    )
                elif media_msg.video:
                    await message.bot.send_video(
                        uid, media_msg.video.file_id, caption=text
                    )
                elif media_msg.document:
                    await message.bot.send_document(
                        uid, media_msg.document.file_id, caption=text
                    )
            else:
                await message.bot.send_message(uid, text)
            success += 1
        except Exception:
            fail += 1

    await message.answer(f"📬 Рассылка завершена. Успешно: {success}, Ошибки: {fail}")
    await state.clear()
