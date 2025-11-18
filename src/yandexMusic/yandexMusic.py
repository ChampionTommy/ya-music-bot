import os
import asyncio
import re
import random
from typing import List, Optional, Tuple, Union
from discord import FFmpegPCMAudio
from yandex_music import ClientAsync, Track, ArtistTracks, ChartInfo
from src.errors.general import (
    ClientNotInitializedError,
    PlaylistEmptyError,
    PlayerError,
    SearchNoFindError,
    LinkInvalidError,
)


class YandexMusic:
    def __init__(self, token: str, save_path: str = "./music"):
        self._token = token
        self._save_path = save_path
        self._client: Optional[ClientAsync] = None
        self._playlist: List[Track] = []

    @property
    def playlist(self) -> List[Track]:
        return self._playlist

    async def init_client(self):
        if self._client is None:
            try:
                self._client = await ClientAsync(self._token).init()
            except Exception as e:
                raise ClientNotInitializedError(f"Ошибка инициализации клиента: {e}")

    async def download_with_retry(self, track, filename, retries=5):
        for attempt in range(retries):
            try:
                await track.download_async(filename)
                return True
            except Exception as e:
                # Ловим лимиты
                if "429" in str(e) or "limited" in str(e):
                    delay = 1.5 + attempt + random.uniform(0, 0.7)
                    print(f"[429] Лимит. Повтор через {delay:.1f} сек")
                    await asyncio.sleep(delay)
                else:
                    raise
        return False

    async def get_next_audio_source(self) -> Tuple[FFmpegPCMAudio, str]:
        if not self._playlist:
            raise PlaylistEmptyError("Очередь воспроизведения пуста")

        track = self._playlist.pop(0)

        os.makedirs(self._save_path, exist_ok=True)
        filename = os.path.join(self._save_path, f"{track.id}_{track.title}.mp3")

        if not os.path.isfile(filename):
            try:
                await track.download_async(filename)
            except Exception as e:
                raise PlayerError(f"Ошибка загрузки трека {track.title}: {e}")

        source = FFmpegPCMAudio(filename)
        title = track.title or "Неизвестный трек"

        async def _delete_after_play():
            await asyncio.sleep(1)  # небольшой delay
            if os.path.exists(filename):
                os.remove(filename)

        asyncio.create_task(_delete_after_play())

        return source, title

    async def add_tracks(self, tracks: List[Track]):
        if not tracks:
            raise PlaylistEmptyError("Список треков пустой")
        self._playlist.extend(tracks)

    async def add_track_by_id(self, track_id: Union[int, str]) -> Track:
        if self._client is None:
            raise ClientNotInitializedError()
        tracks = await self._client.tracks(track_id)
        if not tracks:
            raise SearchNoFindError()
        track = tracks[0]
        self._playlist.append(track)
        return track

    async def add_album(self, album_id: int) -> List[Track]:
        if self._client is None:
            raise ClientNotInitializedError()
        album = await self._client.albums_with_tracks(album_id)
        tracks: List[Track] = []

        if getattr(album, "volumes", None):
            for volume in album.volumes:
                if volume:
                    tracks.extend(volume)
        elif getattr(album, "tracks", None):
            tracks = album.tracks
        else:
            raise PlaylistEmptyError("Не удалось получить треки альбома")

        full_tracks: List[Track] = []
        for t in tracks:
            if hasattr(t, "fetch_track_async"):
                full_tracks.append(await t.fetch_track_async())
            else:
                full_tracks.append(t)

        if not full_tracks:
            raise PlaylistEmptyError("Альбом пустой")

        await self.add_tracks(full_tracks)
        return full_tracks

    async def add_artist(self, link: str, load_all: bool = False) -> List[Track]:
        if self._client is None:
            raise ClientNotInitializedError()

        try:
            artist_id = int(link.rstrip("/").split("/")[-1])
        except ValueError:
            raise SearchNoFindError("Невалидный ID артиста")

        artist_tracks: ArtistTracks = await self._client.artists_tracks(artist_id)
        if not artist_tracks or not artist_tracks.tracks:
            raise SearchNoFindError("У артиста нет треков")

        tracks = artist_tracks.tracks.copy()

        if load_all and artist_tracks.pager:
            while artist_tracks.pager.more:
                page = await artist_tracks.pager.fetch_next()
                tracks.extend(page.tracks)

        await self.add_tracks(tracks)
        return tracks

    async def add_playlist(self, playlist_link: str) -> List[Track]:
        if self._client is None:
            raise ClientNotInitializedError()

        match = re.search(r"/playlists/([a-f0-9-]+)", playlist_link)
        if not match:
            raise LinkInvalidError("Неверный формат ссылки на плейлист")

        playlist_kind = match.group(1)
        playlist_data = await self._client.users_playlists(kind=playlist_kind)
        playlist = (
            playlist_data[0] if isinstance(playlist_data, list) else playlist_data
        )

        if not playlist.tracks:
            raise PlaylistEmptyError("Плейлист пустой")

        tracks = [t.track for t in playlist.tracks if hasattr(t, "track") and t.track]
        await self.add_tracks(tracks)
        return tracks

    async def add_chart(self, chart_option: str = "russia") -> List[Track]:
        if self._client is None:
            raise ClientNotInitializedError()
        chart_info: ChartInfo = await self._client.chart(chart_option)
        if not chart_info or not chart_info.chart:
            raise PlaylistEmptyError("Чарт пустой или недоступен")

        tracks: List[Track] = []
        for t_short in chart_info.chart.tracks:
            if t_short.id is not None:
                track_list = await self._client.tracks(t_short.id)
                if track_list:
                    tracks.append(track_list[0])

        await self.add_tracks(tracks)
        return tracks

    async def clear_playlist(self):
        self._playlist.clear()

    async def link_eater(self, link: str) -> List[Track]:
        if not link.startswith("https://music.yandex.ru/"):
            raise LinkInvalidError()

        if "/track/" in link:
            track_id = int(link.split("/track/")[1].split("?")[0])
            track = await self.add_track_by_id(track_id)
            self._playlist = [track]
            return [track]

        if "/album/" in link and "/track/" not in link:
            album_id = int(link.split("/album/")[1].split("?")[0])
            return await self.add_album(album_id)

        if "/playlists/" in link:
            return await self.add_playlist(link)

        if "/artist/" in link:
            return await self.add_artist(link)

        raise LinkInvalidError()
