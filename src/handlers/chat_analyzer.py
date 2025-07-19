import asyncio
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from keyboards.inline import get_cancel_keyboard, get_style_keyboard
from prompts import (CHAT_ANALYSIS_PROMPT, FIRST_MESSAGE_PROMPT, CHAT_RESCUE_PROMPT,
                     MESSAGE_INTERPRETATION_PROMPT, STYLE_MESSAGE_PROMPT, STYLE_DESCRIPTIONS)
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


@router.callback_query(F.data == "chat_rescue")
async def start_chat_rescue(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_rescue_chat)
    await callback.message.edit_text(
        "🆘 Пришли последние сообщения из диалога (твои и собеседника, 3-5 реплик). "
        "Я дам конкретные инструкции, как спасти ситуацию!",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

# Обработчик для срочной реабилитации
@router.message(AnalysisStates.waiting_for_rescue_chat)
async def process_chat_rescue(message: Message, state: FSMContext):
    await state.clear()
    
    thinking_msg = await message.answer("Анализирую диалог для экстренной помощи...")
    chat_history = message.text
    prompt = CHAT_RESCUE_PROMPT.format(chat_history=chat_history)
    
    ai_response = await get_ai_response(prompt)
    await thinking_msg.delete()
    
    if "Ошибка" in ai_response:
        await message.answer("🚫 Не удалось проанализировать. Убедись, что прислал достаточно контекста.")
    else:
        await safe_send_message(message, ai_response, reply_markup=get_cancel_keyboard())


@router.callback_query(F.data == "interpret_message")
async def start_message_interpretation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_message_interpretation)
    await callback.message.edit_text(
        "💬 Пришли одно сообщение собеседника, которое хочешь расшифровать. "
        "Я разберу скрытые смыслы, эмоции и дам рекомендации!",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AnalysisStates.waiting_for_message_interpretation)
async def process_message_interpretation(message: Message, state: FSMContext):
    await state.clear()
    
    thinking_msg = await message.answer("Анализирую скрытые смыслы...")
    user_message = message.text
    prompt = MESSAGE_INTERPRETATION_PROMPT.format(message=user_message)
    
    ai_response = await get_ai_response(prompt)
    await thinking_msg.delete()
    
    if "Ошибка" in ai_response:
        await message.answer("🚫 Не удалось расшифровать сообщение. Попробуй другое?")
    else:
        await safe_send_message(message, ai_response, reply_markup=get_cancel_keyboard())


@router.callback_query(F.data == "generate_style_message")
async def start_style_generation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_style_context)
    await callback.message.edit_text(
        "💬 Пришли фрагмент переписки (последние 2-3 сообщения), чтобы я мог предложить стили ответа.",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AnalysisStates.waiting_for_style_context)
async def process_style_context(message: Message, state: FSMContext):
    # Сохраняем контекст и переходим к выбору стиля
    await state.update_data(style_context=message.text)
    await state.set_state(AnalysisStates.waiting_for_style_choice)
    
    await message.answer(
        "Отлично! Теперь выбери стиль сообщения:",
        reply_markup=get_style_keyboard()
    )


@router.callback_query(AnalysisStates.waiting_for_style_choice, F.data.startswith("style_"))
async def generate_style_message(callback: CallbackQuery, state: FSMContext):
    style_key = callback.data.split("_")[1]  # "romance", "flirt", и т.д.
    style_name = {
        "romance": "Романтика ❤️",
        "flirt": "Флирт 😏",
        "humor": "Юмор 😄",
        "tease": "Игровой подъёб 😈",
        "sincere": "Искренность ✨",
        "support": "Поддержка 🤗"
    }.get(style_key, "выбранному стилю")
    
    # Получаем сохраненный контекст
    data = await state.get_data()
    chat_context = data.get("style_context", "")
    await state.clear()
    
    if not chat_context:
        await callback.answer("Контекст переписки не найден. Попробуй снова.")
        return
    
    # Индикатор загрузки
    thinking_msg = await callback.message.answer(f"Генерирую сообщения в стиле {style_name}...")
    
    # Формируем промпт с описанием стиля
    style_description = STYLE_DESCRIPTIONS.get(style_key, "")
    prompt = STYLE_MESSAGE_PROMPT.format(
        style=style_name,
        chat_context=chat_context,
        style_description=style_description
    )
    
    ai_response = await get_ai_response(prompt)
    await thinking_msg.delete()
    
    if "Ошибка" in ai_response or not ai_response.strip():
        await callback.message.answer(
            "🚫 Не удалось сгенерировать сообщения. Попробуй другой стиль или контекст."
        )
    else:
        # Отправляем результат
        chunks = split_text(ai_response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                await safe_send_message(
                    callback.message, 
                    chunk, 
                    reply_markup=get_cancel_keyboard()
                )
            else:
                await safe_send_message(callback.message, chunk)
            await asyncio.sleep(0.3)
    
    await callback.answer()