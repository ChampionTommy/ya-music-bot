class PlayerError(Exception):
    """Базовое исключение для плеера"""
    pass

class InvalidTokenError(PlayerError):
    """Неверный токен авторизации"""
    pass

class ConnectionError(PlayerError):
    """Ошибка подключения"""
    pass

class SearchNotFoundError(PlayerError):
    """Треки не найдены"""
    pass

class SearchError(PlayerError):
    """Ошибка поиска"""
    pass

class DownloadError(PlayerError):
    """Ошибка загрузки трека"""
    pass

class AlbumNotFoundError(PlayerError):
    """Альбом не найден"""
    pass

class PlaylistNotFoundError(PlayerError):
    """Плейлист не найден"""
    pass

class PlaylistEmptyError(PlayerError):
    """Плейлист пуст"""
    pass

class InvalidLinkError(PlayerError):
    """Неверная ссылка"""
    pass

class ProcessingError(PlayerError):
    """Ошибка обработки"""
    pass
