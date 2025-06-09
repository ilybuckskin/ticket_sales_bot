from aiogram.utils.keyboard import ReplyKeyboardBuilder


def manager_menu():
    """Клавиатура менеджера"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="📷 Сканировать билет")
    kb.button(text="🔙 Назад")
    kb.button(text="🔙 Завершить сканирование")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
