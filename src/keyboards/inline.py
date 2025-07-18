# keyboards/inline.py
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder




def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 Анализ анкеты", callback_data="analyze_profile")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Анализ переписки", callback_data="analyze_chat")
    )
    builder.row(
        InlineKeyboardButton(text="💌 Первое сообщение", callback_data="generate_first_message")  # Новая кнопка
    )
    builder.row(
        InlineKeyboardButton(text="💡 Помощь и советы", callback_data="help_info")
    )
    return builder.as_markup()


def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="cancel_action")
    )
    return builder.as_markup()