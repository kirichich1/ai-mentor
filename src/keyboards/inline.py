# keyboards/inline.py
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder




def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 Анализ моей анкеты", callback_data="analyze_profile")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Анализ чужой анкеты", callback_data="analyze_other_profile")
    )
    builder.row(
        InlineKeyboardButton(text="✨ Создать анкету", callback_data="generate_profile")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Анализ переписки", callback_data="analyze_chat")
    )
    builder.row(
        InlineKeyboardButton(text="💌 Первое сообщение", callback_data="generate_first_message")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Как отпустить", callback_data="sos_let_go")
    )
    builder.row(
        InlineKeyboardButton(text="💡 Помощь и советы", callback_data="help_info")
    )
    return builder.as_markup()


def get_sos_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Вежливый вариант", callback_data="sos_quick_polite"),
        InlineKeyboardButton(text="Прямой вариант", callback_data="sos_quick_direct")
    )
    builder.row(
        InlineKeyboardButton(text="Простой вариант", callback_data="sos_quick_simple"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="cancel_action")
    )
    return builder.as_markup()


def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="cancel_action")
    )
    return builder.as_markup()