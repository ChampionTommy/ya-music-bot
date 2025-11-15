import asyncio
import os
from discord import FFmpegPCMAudio
from yandex_music import ClientAsync
from player import errors


class Player:
    def __init__(self, token: str, save_path: str = './music/track.mp3'):
        self._save_path = save_path
        self._token = token
        self._loop = asyncio.get_event_loop()
        self._client: ClientAsync = self._loop.run_until_complete(ClientAsync(self._token).init())
        self._playlist = []

    @property
    def playlist(self):
        return self._playlist

    async def search_track(self, query: str):
        """Поиск треков по текстовому запросу"""
        result = await self._client.search(query, type_='track')
        tracks = result.tracks
        if not tracks or len(tracks.results) == 0:
            raise errors.SearchNoFindError()
        return tracks.results

    async def download_track(self, track):
        """Асинхронное скачивание трека"""
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        await track.download_async(self._save_path)
        return self._save_path

    async def get_next(self):
        """Возвращает следующий трек и скачивает его"""
        if not self._playlist:
            raise errors.PlaylistEmptyError()
        track = self._playlist.pop(0)
        path = await self.download_track(track)
        return track, path

    async def get_next_audio_source(self):
        """Возвращает FFmpegPCMAudio для Discord"""
        track, path = await self.get_next()
        return FFmpegPCMAudio(path), track.title

    async def _get_album(self, album_id: int):
        """Получение треков из альбома"""
        album = await self._client.albums_with_tracks(album_id)
        self._playlist = [track for volume in album.volumes for track in volume]
        return self._playlist

    async def _get_playlist(self, link: str):
        """Получение треков из плейлиста любого пользователя"""
        try:
            parts = link.split('/playlists/')
            user = parts[0].split('/')[-1]
            playlist_id = int(parts[1].split('?')[0])
        except Exception:
            raise errors.LinkInvalidError()

        playlist = await (await self._client.playlists_list(f"{user}:{playlist_id}"))[0].fetch_tracks_async()
        self._playlist = [await track.fetch_track_async() for track in playlist]
        return self._playlist

    async def _get_track_by_id(self, track_id: int):
        """Получение отдельного трека по ID"""
        track = await self._client.tracks(track_id)
        if not track:
            raise errors.SearchNoFindError()
        return track[0]

    async def link_eater(self, link: str):
        """
        Универсальная обработка ссылок Яндекс Музыки:
        - Отдельный трек: https://music.yandex.ru/album/ALBUM_ID/track/TRACK_ID
        - Альбом: https://music.yandex.ru/album/ID
        - Плейлист: https://music.yandex.ru/users/USER/playlists/ID
        """
        if 'https://music.yandex.ru/' not in link:
            raise errors.LinkInvalidError()

        # Обработка отдельного трека
        if '/track/' in link:
            try:
                track_id = int(link.split('/track/')[1].split('?')[0])
                track = await self._get_track_by_id(track_id)
                self._playlist = [track]
                return self._playlist
            except Exception:
                raise errors.LinkInvalidError()

        # Обработка альбома
        if '/album/' in link:
            try:
                # Берем только ID альбома (до /track/ если есть)
                album_part = link.split('/album/')[1].split('?')[0]
                album_id = int(album_part.split('/')[0])  # Берем только первую часть до слеша
                return await self._get_album(album_id)
            except Exception:
                raise errors.LinkInvalidError()

        # Обработка плейлиста
        if '/playlists/' in link:
            return await self._get_playlist(link)

        raise errors.LinkInvalidError()