import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_cancel_keyboard
from prompts import PROFILE_ANALYSIS_PROMPT, PROFILE_GENERATOR_PROMPT
from utils.ai_api import split_text, get_ai_response
from utils.states import AnalysisStates
from utils.telegram_helpers import safe_send_message  # Добавляем импорт

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


@router.callback_query(F.data == "generate_profile")
async def start_profile_generation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_user_info)
    await callback.message.edit_text(
        "✨ Отлично! Расскажи о себе в свободной форме:\n"
        "- Возраст, род занятий\n"
        "- Интересы/хобби\n"
        "- Что ищешь в отношениях?\n"
        "- Любые детали, которые хочешь отразить\n\n"
        "Я создам анкету, которая выделит тебя из толпы!",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(AnalysisStates.waiting_for_user_info)
async def generate_profile(message: Message, state: FSMContext):
    await state.clear()
    
    thinking_msg = await message.answer("Создаю твою идеальную анкету... ✨")
    user_info = message.text
    prompt = PROFILE_GENERATOR_PROMPT.format(user_info=user_info)
    
    ai_response = await get_ai_response(prompt)
    await thinking_msg.delete()
    
    if "Ошибка" in ai_response:
        await message.answer("🚫 Не удалось создать анкету. Попробуй описать себя подробнее.")
    else:
        await safe_send_message(message, ai_response, reply_markup=get_cancel_keyboard())