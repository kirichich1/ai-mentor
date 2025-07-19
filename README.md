### Инструкция по запуску

  1. **Установить Python** (у нас версия 3.11)

  2. **Создать виртуальное окружение**  
     ```bash
     python -m venv venv
     venv/Scripts/activate
     ```

  3. **Установить зависимости**  
     ```bash
     pip install -r requirements.txt
     ```

  4. **Создать файл `.env`** (внутри папки `src`)

  5. **Заполнить `.env`** Скопировать туда содержимое файла `secrets.txt`, который мы прислали вместе с презентацией

  6. **Запустить бота**  
     ```bash
     cd src
     python __main__.py
     ```

  7. **Пользоваться ботом** В Telegram: [@DatingMentorBot](https://t.me/DatingMentorBot).