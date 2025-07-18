# handlers/common.py
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.keyboards.inline import get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        "Я твой ИИ-ментор по дейтингу **Q-pid**. Готов помочь тебе стать звездой онлайн-знакомств.\n\n"
        "Чем займемся сегодня?",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "cancel_action")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        logging.info(f"Отмена состояния {current_state} для пользователя {callback.from_user.id}")
        await state.clear()

    await callback.message.edit_text(
        "Вы вернулись в главное меню. Чем могу помочь?",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "help_info")
async def help_info_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "💡 **Краткая инструкция:**\n\n"
        "**🔍 Анализ анкеты:**\n"
        "Пришли мне полный текст своей анкеты с сайта знакомств. Я проанализирую её и дам советы, как сделать её в 10 раз привлекательнее.\n\n"
        "**💬 Анализ переписки:**\n"
        "Скопируй и пришли 2-3 последних сообщения из своего диалога (твои и собеседника). Я подскажу, куда двигаться дальше и как исправить возможные ошибки.\n\n"
        "Нажми 'Назад', чтобы вернуться в меню.",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()