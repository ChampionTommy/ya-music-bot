

class AudioAlreadyPlayError(Exception):
    def __init__(self):
        super().__init__()


class AudioAlreadyPauseError(Exception):
    def __init__(self):
        super().__init__()


class AudioNoTrackError(Exception):
    def __init__(self):
        super().__init__()
