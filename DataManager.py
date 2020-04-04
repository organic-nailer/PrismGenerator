import threading

#appとuiを色んなところで使うのでSingletonで保持


class Manager:
    _instance = None
    _lock = threading.Lock()
    _app = None
    _ui = None

    def __init__(self):
        print('init')

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)

        return cls._instance

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value

    @property
    def ui(self):
        return self._ui

    @ui.setter
    def ui(self, value):
        self._ui = value
