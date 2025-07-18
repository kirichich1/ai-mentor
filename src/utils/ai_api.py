import aiohttp
import asyncio
import logging
from aiocache import cached


from src.config import OPENROUTER_API_KEY, OPENROUTER_API_URL, MODEL_NAME, SITE_NAME


# Настройка кеша: 200 записей, время жизни - 1 час (3600 секунд)

async def get_ai_response(prompt: str) -> str:
    """
    Асинхронно отправляет запрос к API OpenRouter и возвращает ответ.
    Использует кеширование для ускорения повторных запросов.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Рекомендуемые заголовки для OpenRouter для идентификации вашего проекта
        "HTTP-Referer": f"https://t.me/your_bot_username",  # Замените на имя вашего бота
        "X-Title": SITE_NAME,
    }

    # Структура payload для OpenRouter (OpenAI-совместимая)
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=120) as response:
                if response.status == 200:
                    data = await response.json()
                    # Извлекаем ответ из новой структуры
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        return content.strip()
                    else:
                        logging.error(f"API OpenRouter: Неожиданный формат ответа: {data}")
                        return "Ошибка: Не удалось извлечь текст из ответа API."
                else:
                    error_text = await response.text()
                    logging.error(f"API OpenRouter: Ошибка {response.status}: {error_text}")
                    return f"Ошибка при обращении к API: {response.status}. Попробуйте позже."
    except asyncio.TimeoutError:
        logging.error("API OpenRouter: Таймаут запроса")
        return "Ошибка: Сервер ИИ слишком долго отвечает. Пожалуйста, попробуйте позже."
    except aiohttp.ClientError as e:
        logging.error(f"Сетевая ошибка при запросе к API OpenRouter: {e}")
        return "Сетевая ошибка. Проверьте ваше подключение или попробуйте позже."


# utils/ai_api.py

def split_text(text: str, chunk_size: int = 4000) -> list[str]:
    """
    "Умная" разбивка длинного текста на части, не превышающие лимит Telegram.
    Старается не разрывать Markdown-сущности (жирный, курсив, код).
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    text_remaining = text

    # Список парных тегов Markdown
    markdown_tags = ["**", "*", "__", "_", "`", "```"]

    while len(text_remaining) > chunk_size:
        # Ищем идеальную точку для разрыва, двигаясь от конца чанка к началу
        split_pos = text_remaining.rfind('\n', 0, chunk_size)
        if split_pos == -1:
            split_pos = text_remaining.rfind(' ', 0, chunk_size)
        if split_pos == -1:
            split_pos = chunk_size

        # Проверяем, сбалансированы ли теги в куске, который мы хотим отрезать
        is_balanced = False
        while not is_balanced:
            chunk_to_check = text_remaining[:split_pos]

            # Проверяем баланс для каждого тега
            balanced_for_all_tags = True
            for tag in markdown_tags:
                if chunk_to_check.count(tag) % 2 != 0:
                    balanced_for_all_tags = False
                    break

            if balanced_for_all_tags:
                is_balanced = True
            else:
                # Если дисбаланс, ищем предыдущий перенос строки или пробел
                new_split_pos = text_remaining.rfind('\n', 0, split_pos - 1)
                if new_split_pos == -1:
                    new_split_pos = text_remaining.rfind(' ', 0, split_pos - 1)

                if new_split_pos == -1:
                    # Не удалось найти безопасное место, разрываем как есть,
                    # чтобы избежать бесконечного цикла
                    is_balanced = True
                else:
                    split_pos = new_split_pos

        chunks.append(text_remaining[:split_pos])
        text_remaining = text_remaining[split_pos:].lstrip()

    if text_remaining:
        chunks.append(text_remaining)

    return chunks