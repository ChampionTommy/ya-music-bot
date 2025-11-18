import asyncio
from typing import Optional, List
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

from src.errors.general import ChannelNoVoiceError
from src.errors.messages import Messages
from src.yandexMusic.yandexMusic import YandexMusic


class BotDiscord:
    def __init__(
        self,
        token: str,
        command_prefix: str,
        intents: discord.Intents,
        player: YandexMusic,
    ):
        self._token = token
        self._player = player
        self._bot = commands.Bot(command_prefix=command_prefix, intents=intents)
        self._voice: Optional[discord.VoiceClient] = None
        self._queue_lock = asyncio.Lock()
        self._skip_event = asyncio.Event()
        self._current_play_task: Optional[asyncio.Task] = None
        self.init_handlers()

    async def get_voice(self, ctx: commands.Context) -> discord.VoiceClient:
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            raise ChannelNoVoiceError()
        if self._voice is None or self._voice.channel != ctx.author.voice.channel:
            if self._voice is not None:
                await self._voice.disconnect()
            self._voice = await ctx.author.voice.channel.connect()
        return self._voice

    async def play_loop(self, ctx: commands.Context):
        while True:
            # Если плейлист пуст — выходим
            if not self._player.playlist:
                self._current_play_task = None
                return

            # Берём трек
            async with self._queue_lock:
                try:
                    source, title = await self._player.get_next_audio_source()
                except Exception as e:
                    print(f"[Ошибка при получении трека]: {e}", flush=True)
                    continue

            await ctx.send(f"Сейчас играет: {title}", mention_author=False)

            # Проверяем голос
            if not self._voice:
                await ctx.send(
                    "Бот не подключён к голосовому каналу", mention_author=False
                )
                self._current_play_task = None
                return

            # Сбрасываем skip
            self._skip_event.clear()

            # Если уже играет — стоп
            if self._voice.is_playing() or self._voice.is_paused():
                self._voice.stop()

            # Воспроизведение
            self._voice.play(source)

            # Ждём окончания трека или skip
            while True:
                # skip
                if self._skip_event.is_set():
                    self._skip_event.clear()
                    if self._voice.is_playing():
                        self._voice.stop()
                    break

                # трек закончился
                if not self._voice.is_playing():
                    break

                await asyncio.sleep(0.3)

            # Выход из цикла
            self._current_play_task = None

    def start_new_playback(self, ctx: commands.Context):
        if not self._current_play_task or self._current_play_task.done():
            self._current_play_task = asyncio.create_task(self.play_loop(ctx))
        else:
            self._skip_event.set()

    async def start_new_playlist(self, ctx: commands.Context, tracks: List):
        """Перезапускает loop с новыми треками"""
        if self._current_play_task and not self._current_play_task.done():
            self._skip_event.set()
            self._current_play_task.cancel()
            self._current_play_task = None

        if self._voice and self._voice.is_playing():
            self._voice.stop()

        self._player.playlist.clear()

        await self._player.add_tracks(tracks)

        self.start_new_playback(ctx)

    def init_handlers(self):
        @self._bot.event
        async def on_ready():
            if self._player._client is None:
                await self._player.init_client()
                print("[ЯМ] Яндекс Музыка клиент инициализирован")
            print(f"[Бот] {self._bot.user} успешно запущен!")

        async def handle_command(ctx: commands.Context, tracks: List):
            try:
                await self.get_voice(ctx)
                if not tracks:
                    await ctx.send("Не удалось загрузить треки", mention_author=False)
                    return
                await self.start_new_playlist(ctx, tracks)
            except ChannelNoVoiceError:
                await ctx.reply(Messages["discord"]["no_voice_channel"])
            except Exception as e:
                import traceback

                await ctx.reply(Messages["discord"]["unknown"])
                print(f"[Ошибка команды]: {e}")
                traceback.print_exc()

        @self._bot.command()
        async def queue(ctx: commands.Context, *, link: str):
            tracks = await self._player.link_eater(link)
            await handle_command(ctx, tracks)

        @self._bot.command()
        async def play(ctx: commands.Context, *, link: str):
            tracks = await self._player.link_eater(link)
            await handle_command(ctx, tracks)

        @self._bot.command()
        async def artist(ctx: commands.Context, *, link: str):
            tracks = await self._player.add_artist(link)
            await handle_command(ctx, tracks)

        @self._bot.command()
        async def chart(ctx: commands.Context, *, region: str = "russia"):
            tracks = await self._player.add_chart(chart_option=region)
            await handle_command(ctx, tracks)

        @self._bot.command()
        async def skip(ctx: commands.Context):
            if self._voice and (self._voice.is_playing() or self._skip_event.is_set()):
                self._skip_event.set()
                await ctx.reply("Трек пропущен!", mention_author=False)
            else:
                await ctx.reply("Сейчас ничего не играет.", mention_author=False)

        @self._bot.command()
        async def stop(ctx: commands.Context):
            if self._current_play_task and not self._current_play_task.done():
                self._skip_event.set()
                self._current_play_task.cancel()
                self._current_play_task = None

            if self._voice and self._voice.is_playing():
                self._voice.stop()

            self._player.playlist.clear()
            await ctx.send("Воспроизведение остановлено!", mention_author=False)

        @self._bot.command()
        async def nowplaying(ctx: commands.Context):
            if (
                self._current_play_task
                and not self._current_play_task.done()
                and self._player.playlist
            ):
                await ctx.send("Сейчас играет трек из очереди", mention_author=False)
            else:
                await ctx.send("Сейчас ничего не играет", mention_author=False)

    def run(self):
        self._bot.run(self._token)
