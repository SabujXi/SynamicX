class UploadManager:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__uploaders_map = {}
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    def load(self):
        self.__install_builtin_uploaders()
        self.__is_loaded = True

    def __install_builtin_uploaders(self):
        from .builtin_uploaders.firebase_uploader import FireBaseUploader
        self.add_uploader('firebase', FireBaseUploader)

    def add_uploader(self, name, uploader_class):
        assert type(uploader_class) is type
        assert name not in self.__uploaders_map
        self.__uploaders_map[name] = uploader_class(self.__synamic)

    def get_uploader(self, name, default=None):
        return self.__uploaders_map.get(name, default)
