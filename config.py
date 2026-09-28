"""Конфигурация бота: все настройки берутся только из переменных окружения."""
import os
import sys

BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "").strip()
DB_PATH: str = os.environ.get("DB_PATH", "shop.db")
ADMIN_ID: int = int(os.environ.get("ADMIN_ID", "0") or 0)


def require_token() -> str:
    """Возвращает BOT_TOKEN, при отсутствии завершает работу с понятным сообщением."""
    if not BOT_TOKEN:
        print(
            "Ошибка: не задан токен бота (переменная окружения BOT_TOKEN).\n"
            "1. Создайте бота у @BotFather и скопируйте токен.\n"
            '2. Установите токен:  Windows (PowerShell):  $env:BOT_TOKEN = "123456:ABC-DEF"\n'
            '                      Linux / macOS:         export BOT_TOKEN="123456:ABC-DEF"\n'
            "3. Запустите бота снова: python bot.py"
        )
        sys.exit(1)
    return BOT_TOKEN
