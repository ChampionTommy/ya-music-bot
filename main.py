import os
import sys
import discord
from dotenv import load_dotenv

from bot import BotDiscord
from player import Player

load_dotenv()


def get_env_variable(name: str, default: str | None = None) -> str:
    """Получение переменной окружения. Выбрасывает ошибку, если переменная не задана и нет default"""
    value = os.getenv(name)
    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f"Не задана переменная окружения: {name}")
    return value


def create_player() -> Player:
    token = get_env_variable("YANDEX_MUSIC_TOKEN")
    return Player(token)


def create_bot(player: Player) -> BotDiscord:
    token = get_env_variable("DISCORD_BOT_TOKEN")
    command_prefix = get_env_variable("DISCORD_BOT_COMMAND_PREFIX", "/")
    intents = discord.Intents.default()
    intents.message_content = True
    return BotDiscord(token, command_prefix, intents, player)


def check_yam_token(player: Player) -> bool:
    """Простая проверка токена Яндекс Музыки"""
    try:
        if player._client is None:
            raise ValueError("Клиент не инициализирован")
        print("[ЯМ] Подключение к Яндекс Музыке успешно (токен валидный).")
        return True
    except Exception as e:
        print(f"[ЯМ] Ошибка подключения: {e}")
        return False


def main() -> None:
    try:
        player = create_player()
    except RuntimeError as e:
        print(f"[Ошибка] {e}")
        sys.exit(1)

    if not check_yam_token(player):
        print("[Бот] Завершение запуска из-за ошибки с Яндекс Музыкой.")
        sys.exit(1)

    try:
        bot = create_bot(player)
        bot.run()
    except RuntimeError as e:
        print(f"[Бот] Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
