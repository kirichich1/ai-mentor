# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# Импортируем конфигурацию и обработчики
from config import BOT_TOKEN, PROXY_URL
from handlers import common, profile_analyzer, chat_analyzer

async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Starting bot...")

    # Инициализация бота
    # Если используется прокси, раскомментируйте следующую строку
    # from aiogram.client.session.aiohttp import AiohttpSession
    # session = AiohttpSession(proxy=PROXY_URL)
    # bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    # Стандартная инициализация без прокси
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    # Инициализация диспетчера и хранилища FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение роутеров
    dp.include_router(common.router)
    dp.include_router(profile_analyzer.router)
    dp.include_router(chat_analyzer.router)

    # Удаление вебхука перед запуском (на случай, если он был установлен)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск поллинга
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")