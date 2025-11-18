class PlayerError(Exception):
    def __init__(self, message: str = "Ошибка плеера"):
        self.message = message
        super().__init__(self.message)


class LinkInvalidError(PlayerError):
    def __init__(self, message: str = "Неверная ссылка"):
        self.message = message


class PlaylistEmptyError(PlayerError):
    def __init__(self, message: str = "Плейлист пустой"):
        self.message = message
        super().__init__(self.message)


class SearchNoFindError(PlayerError):
    def __init__(self, message: str = "Ничего не найдено"):
        self.message = message
        super().__init__(self.message)


class DownloadError(PlayerError):
    def __init__(self, message: str = "Ошибка загрузки трека"):
        self.message = message
        super().__init__(self.message)


class ClientNotInitializedError(PlayerError):
    def __init__(self, message: str = "Клиент не инициализирован"):
        self.message = message
        super().__init__(self.message)


class ChannelNoVoiceError(PlayerError):
    def __init__(self, message: str = "Пользователь не в голосовом канале"):
        self.message = message
        super().__init__(self.message)


class VoiceConnectionError(PlayerError):
    def __init__(self, message: str = "Ошибка подключения к голосовому каналу"):
        self.message = message
        super().__init__(self.message)


class AudioPlaybackError(PlayerError):
    def __init__(self, message: str = "Ошибка воспроизведения аудио"):
        self.message = message
        super().__init__(self.message)
