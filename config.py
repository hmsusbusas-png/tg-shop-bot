"""Конфигурация бота: все настройки берутся только из переменных окружения."""
import os
import sys

BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "").strip()
DB_PATH: str = os.environ.get("DB_PATH", "shop.db")


def _parse_admin_id(raw: str) -> int:
    """ADMIN_ID должен быть числом; иначе объясняем, как исправить, и выходим."""
    raw = (raw or "").strip()
    if not raw:
        return 0
    try:
        return int(raw)
    except ValueError:
        print(
            f"Ошибка: ADMIN_ID должен быть целым числом, получено: {raw!r}.\n"
            "Узнать свой числовой id можно у @userinfobot, затем задайте без пробелов:\n"
            '  Windows (PowerShell):  $env:ADMIN_ID = "123456789"\n'
            '  Linux / macOS:         export ADMIN_ID=123456789'
        )
        sys.exit(1)


ADMIN_ID: int = _parse_admin_id(os.environ.get("ADMIN_ID", ""))


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
