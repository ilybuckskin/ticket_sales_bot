from aiogram import Router, types
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from sqlalchemy.future import select

from bot.keyboards.admin import admin_menu, event_menu
from bot.keyboards.manager import manager_menu
from bot.middlewares.admin_check import AdminMiddleware
from core.database import AsyncSessionLocal
from core.models import User

router = Router()
router.message.middleware(AdminMiddleware())


@router.message(
    lambda message: message.text and "Управление мероприятиями" in message.text
)
async def manage_events(message: types.Message, command: CommandObject | None = None):
    """Открывает меню управления мероприятиями"""
    await message.answer("🎭 Управление мероприятиями:", reply_markup=event_menu())
