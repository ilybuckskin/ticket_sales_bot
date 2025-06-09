from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_menu():
    """Клавиатура админ-панели"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="📅 Управление мероприятиями")
    kb.button(text="📢 Рассылка")
    kb.button(text="👥 Пользователи")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def event_menu():
    """Клавиатура управления мероприятиями"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Добавить мероприятие")
    kb.button(text="🗑 Удалить мероприятие")
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def user_menu():
    """Клавиатура управления пользователями"""
    kb = ReplyKeyboardBuilder()
    kb.button(text="📋 Список пользователей")
    kb.button(text="🚫 Заблокировать пользователя")
    kb.button(text="👑 Назначить менеджера")
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
