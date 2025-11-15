import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

from .errors import (
    ChannelNoVoiceError,
)
from .answers import messages
from player.errors import SearchNoFindError
from player import Player


def pretty_duration(duration) -> str:
    minutes = int(duration / 60000)
    seconds = int(duration % 60000) // 1000
    return f"{minutes:02d}:{seconds:02d}"


class BotDiscord:
    def __init__(
        self, token: str, command_prefix: str, intents: discord.Intents, player: Player
    ):
        self._token = token
        self._player = player
        self._bot = commands.Bot(command_prefix=command_prefix, intents=intents)
        self._statuses = dict()
        self.init_handlers()

    async def get_voice(self, ctx):
        """Подключение к голосовому каналу автора команды"""
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            raise ChannelNoVoiceError()
        if (
            ctx.voice_client is None
            or ctx.voice_client.channel != ctx.author.voice.channel
        ):
            return await ctx.author.voice.channel.connect()
        return ctx.voice_client

    def init_handlers(self):
        """Инициализация обработчиков"""

        @self._bot.event
        async def on_ready():
            print(f"[Бот] {self._bot.user} успешно запущен!")

        # Команда queue — проигрывает всю очередь из альбома/плейлиста
        @self._bot.command()
        async def queue(ctx: commands.Context, *, link: str):
            try:
                voice = await self.get_voice(ctx)
                await self._player.link_eater(link)
                self._statuses[ctx.guild.id] = {"break": False}

                # Проигрываем треки, пока плейлист не пустой
                while self._player.playlist:
                    if self._statuses[ctx.guild.id]["break"]:
                        break

                    source, title = await self._player.get_next_audio_source()
                    await ctx.reply(f"Сейчас играет: {title}", mention_author=False)

                    if voice.is_playing():
                        voice.stop()

                    # Ждём окончания трека
                    loop = asyncio.get_running_loop()
                    future = loop.create_future()

                    def after_playing(error):
                        if error:
                            print(f"[Ошибка воспроизведения]: {error}")
                        if not future.done():
                            future.set_result(True)

                    voice.play(source, after=after_playing)
                    await future

                # Отключение после завершения очереди
                if voice.is_connected():
                    await voice.disconnect()
                if ctx.guild.id in self._statuses:
                    del self._statuses[ctx.guild.id]

            except ChannelNoVoiceError:
                await ctx.reply(messages["discord"]["no_voice_channel"])
            except SearchNoFindError:
                await ctx.reply(messages["player"]["no_track"])
            except Exception as e:
                await ctx.reply(messages["discord"]["unknown"])
                print(f"[Ошибка команды queue]: {e}")

        # Команда play — проигрывает только один трек
        @self._bot.command()
        async def play(ctx: commands.Context, *, link: str):
            try:
                voice = await self.get_voice(ctx)
                await self._player.link_eater(link)
                track = self._player.playlist[0]  # берем только первый трек
                source, title = await self._player.get_next_audio_source()

                if voice.is_playing():
                    voice.stop()

                loop = asyncio.get_running_loop()
                future = loop.create_future()

                def after_playing(error):
                    if error:
                        print(f"[Ошибка воспроизведения]: {error}")
                    if not future.done():
                        future.set_result(True)

                voice.play(source, after=after_playing)
                await ctx.reply(f"Сейчас играет: {title}", mention_author=False)
                await future  # ждём окончания трека

                if voice.is_connected():
                    await voice.disconnect()

            except ChannelNoVoiceError:
                await ctx.reply(messages["discord"]["no_voice_channel"])
            except SearchNoFindError:
                await ctx.reply(messages["player"]["no_track"])
            except Exception as e:
                await ctx.reply(messages["discord"]["unknown"])
                print(f"[Ошибка команды play]: {e}")

    def run(self):
        self._bot.run(self._token)
