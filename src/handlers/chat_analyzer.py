import asyncio
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards.inline import get_cancel_keyboard
from prompts import CHAT_ANALYSIS_PROMPT, FIRST_MESSAGE_PROMPT
from utils.ai_api import split_text, get_ai_response
from utils.states import AnalysisStates

router = Router()


@router.callback_query(F.data == "analyze_chat")
async def start_chat_analysis(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_chat)
    await callback.message.edit_text(
        "Принято! Пришли мне 2-3 последних сообщения из переписки (и твои, и собеседника). 💬",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


async def safe_send_message(message: Message, text: str, reply_markup=None):
    """Безопасная отправка сообщения с автоматическим fallback при ошибке Markdown."""
    try:
        # Пытаемся отправить с Markdown
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "can't parse entities" in str(e):
            # Если ошибка в разметке, удаляем все Markdown-теги и отправляем заново
            clean_text = re.sub(r'[*_`]', '', text)  # Удаляем *, _, `
            clean_text = re.sub(r'```[^`]*```', lambda m: m.group(0).replace('```', ''), clean_text)  # Убираем блоки кода
            await message.answer(clean_text, reply_markup=reply_markup)
        else:
            # Если другая ошибка, пробрасываем дальше
            raise e


@router.message(AnalysisStates.waiting_for_chat)
async def process_chat(message: Message, state: FSMContext):
    await state.clear()

    thinking_message = await message.answer("Анализирую переписку... 🕵️‍♂️ Дай мне минутку.")

    user_chat_text = message.text
    prompt = CHAT_ANALYSIS_PROMPT.format(user_chat=user_chat_text)

    ai_response = await get_ai_response(prompt)

    await thinking_message.delete()

    if "Ошибка" in ai_response:
        await message.answer(
            f"🚫 Произошла ошибка:\n\n`{ai_response}`\n\n"
            "Пожалуйста, попробуй еще раз."
        )
    else:
        chunks = split_text(ai_response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                # Используем безопасную отправку для последнего чанка с клавиатурой
                await safe_send_message(message, chunk, reply_markup=get_cancel_keyboard())
            else:
                # Используем безопасную отправку для остальных чанков
                await safe_send_message(message, chunk)
            await asyncio.sleep(0.5)


# Новый обработчик для генерации первого сообщения
@router.callback_query(F.data == "generate_first_message")
async def start_first_message_generation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_target_profile)
    await callback.message.edit_text(
        "💌 Отлично! Пришли мне анкету человека, которому хочешь написать. "
        "Я придумаю несколько вариантов первого сообщения, от которого невозможно не ответить!",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

# Обработчик получения анкеты собеседника
@router.message(AnalysisStates.waiting_for_target_profile)
async def generate_first_message(message: Message, state: FSMContext):
    await state.clear()

    # Индикатор загрузки
    thinking_message = await message.answer("Генерирую варианты первого сообщения... 💌")

    target_profile = message.text
    prompt = FIRST_MESSAGE_PROMPT.format(target_profile=target_profile)

    # Запрос к API
    ai_response = await get_ai_response(prompt)

    # Удаляем индикатор загрузки
    await thinking_message.delete()

    if "Ошибка" in ai_response:
        await message.answer(
            f"🚫 Произошла ошибка:\n\n`{ai_response}`\n\n"
            "Пожалуйста, попробуй еще раз."
        )
    else:
        chunks = split_text(ai_response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                await safe_send_message(message, chunk, reply_markup=get_cancel_keyboard())
            else:
                await safe_send_message(message, chunk)
            await asyncio.sleep(0.5)