from aiogram import Router, types
from aiogram.filters.command import CommandObject

from bot.middlewares.admin_check import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())


@router.message(lambda message: message.text and "Пользователи" in message.text)
async def manage_users(message: types.Message, command: CommandObject | None = None):
    """Меню управления пользователями"""
    from bot.keyboards.admin import user_menu

    await message.answer("👥 Управление пользователями:", reply_markup=user_menu())
