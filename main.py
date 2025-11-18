import os
import sys

import discord
from dotenv import load_dotenv

from src.botDiscord import BotDiscord
from src.yandexMusic import YandexMusic

load_dotenv()


def get_env_variable(name: str, default: str | None = None) -> str:
    value = os.getenv(name)
    if value is None:
        if default is not None:
            return default
        raise RuntimeError(f"Не задана переменная окружения: {name}")
    return value


def create_player() -> YandexMusic:
    token = get_env_variable("YANDEX_MUSIC_TOKEN")
    return YandexMusic(token)


def create_bot(player: YandexMusic) -> BotDiscord:
    token = get_env_variable("DISCORD_BOT_TOKEN")
    command_prefix = get_env_variable("DISCORD_BOT_COMMAND_PREFIX", "/")
    intents = discord.Intents.default()
    intents.message_content = True
    return BotDiscord(token, command_prefix, intents, player)


def main():
    try:
        player = create_player()
        bot = create_bot(player)
        bot.run()  # Discord создаёт свой event loop
    except RuntimeError as e:
        print(f"[Бот] Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
