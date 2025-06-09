from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu():
    """Генерируем главное меню"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎟 Купить билет")
    kb.button(text="🎫 Мои билеты")
    kb.button(text="📞 Связаться с менеджером")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)
