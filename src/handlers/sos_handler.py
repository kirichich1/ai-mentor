import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import get_cancel_keyboard, get_sos_options_keyboard
from prompts import SOS_LET_GO_PROMPT
from utils.states import AnalysisStates
from utils.telegram_helpers import safe_send_message
from utils.ai_api import get_ai_response, split_text

router = Router()

@router.callback_query(F.data == "sos_let_go")
async def start_sos_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AnalysisStates.waiting_for_sos_context)
    
    await callback.message.edit_text(
        "🆘 Расскажи в двух словах о ситуации:\n"
        "- Как долго общаетесь?\n"
        "- На какой стадии знакомство?\n"
        "- Почему хочешь завершить диалог?\n\n"
        "Это поможет мне предложить самые подходящие варианты.",
        reply_markup=get_sos_options_keyboard()
    )
    await callback.answer()

@router.message(AnalysisStates.waiting_for_sos_context)
async def generate_let_go_options(message: Message, state: FSMContext):
    await state.clear()
    
    # Индикатор загрузки
    thinking_msg = await message.answer("Готовлю вежливые варианты...")
    
    context = message.text
    prompt = SOS_LET_GO_PROMPT.format(context=context)
    
    ai_response = await get_ai_response(prompt)
    await thinking_msg.delete()
    
    if "Ошибка" in ai_response:
        await message.answer(
            f"🚫 Произошла ошибка:\n\n{ai_response}\n\n"
            "Попробуй описать ситуацию короче."
        )
    else:
        chunks = split_text(ai_response)
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                await safe_send_message(
                    message, 
                    chunk + "\n\n👇 Выбери вариант или вернись в меню:",
                    reply_markup=get_sos_options_keyboard()
                )
            else:
                await safe_send_message(message, chunk)
            await asyncio.sleep(0.3)

# Обработчик для быстрых вариантов без контекста
@router.callback_query(F.data.startswith("sos_quick_"))
async def quick_sos_option(callback: CallbackQuery):
    option_type = callback.data.split("_")[-1]
    
    responses = {
        "polite": "🙏 Быстрый вариант: \"Благодарю за общение! Пока что не готов/а продолжать диалог, но желаю удачи в поисках!\"",
        "direct": "✋ Быстрый вариант: \"Привет! Спасибо за беседу, но чувствую, что не совпадаем. Желаю найти того, кто оценит тебя по достоинству!\"",
        "simple": "👋 Быстрый вариант: \"Привет! Спасибо за общение, но не вижу смысла продолжать диалог. Всего хорошего!\""
    }
    
    await callback.message.edit_text(
        responses.get(option_type, responses["polite"]),
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()