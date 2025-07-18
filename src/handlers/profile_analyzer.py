import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.keyboards.inline import get_cancel_keyboard
from src.prompts import PROFILE_ANALYSIS_PROMPT
from src.utils.ai_api import split_text, get_ai_response
from src.utils.states import AnalysisStates
from src.utils.telegram_helpers import safe_send_message  # Добавляем импорт

router = Router()


@router.callback_query(F.data == "analyze_profile")
async def start_profile_analysis(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_profile)
    await callback.message.edit_text(
        "Отлично! Пришли мне текст своей анкеты. Я жду. ✍️",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AnalysisStates.waiting_for_profile)
async def process_profile(message: Message, state: FSMContext):
    await state.clear()

    # Индикатор загрузки
    thinking_message = await message.answer("Анализирую твою анкету... ⏳ Это может занять до минуты.")

    user_profile_text = message.text
    prompt = PROFILE_ANALYSIS_PROMPT.format(user_profile=user_profile_text)

    # Запрос к API
    ai_response = await get_ai_response(prompt)

    # Удаляем индикатор загрузки
    await thinking_message.delete()

    if "Ошибка" in ai_response:
        await message.answer(
            f"🚫 Произошла ошибка:\n\n`{ai_response}`\n\n"
            "Пожалуйста, попробуй еще раз. Если ошибка повторяется, возможно, API временно недоступен."
        )
    else:
        # Разбиваем длинный ответ на частиs
        chunks = split_text(ai_response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:  # Для последнего сообщения добавляем кнопку "назад"
                await safe_send_message(message, chunk, reply_markup=get_cancel_keyboard())
            else:
                await safe_send_message(message, chunk)
            await asyncio.sleep(0.5)  # Небольшая задержка между сообщениями