from aiogram import Router, types
from aiogram.filters import Command

from ..keyboards.admin import admin_menu
from ..middlewares.admin_check import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer(
        "🔧 Админ-панель. Выберите действие:", reply_markup=admin_menu()
    )
