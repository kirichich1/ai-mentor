# src/utils/telegram_helpers.py
import re
import logging
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest


async def safe_send_message(message: Message, text: str, reply_markup=None):
    """
    Безопасная отправка сообщения с автоматическим fallback при ошибке Markdown.
    """
    try:
        # Пытаемся отправить с Markdown
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "can't parse entities" in str(e):
            logging.warning(f"Ошибка Markdown, отправляем без разметки: {e}")
            # Удаляем все Markdown-теги и отправляем заново
            clean_text = clean_markdown_text(text)
            await message.answer(clean_text, reply_markup=reply_markup)
        else:
            # Если другая ошибка, пробрасываем дальше
            raise e


def clean_markdown_text(text: str) -> str:
    """
    Удаляет всю Markdown-разметку из текста.
    """
    # Удаляем жирный текст (**)
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)

    # Удаляем курсив (*)
    text = re.sub(r'\*([^*]*)\*', r'\1', text)

    # Удаляем подчеркивание (__)
    text = re.sub(r'__([^_]*)__', r'\1', text)

    # Удаляем подчеркивание (_)
    text = re.sub(r'_([^_]*)_', r'\1', text)

    # Удаляем инлайн-код (`)
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # Удаляем блоки кода (```)
    text = re.sub(r'```[^`]*```', lambda m: m.group(0).replace('```', ''), text)

    # Удаляем оставшиеся одиночные символы разметки
    text = re.sub(r'[*_`]', '', text)

    return text