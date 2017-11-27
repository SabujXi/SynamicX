import mimetypes
from synamic.core.classes.url import Url
from synamic.core.contracts import ContentContract, ContentModuleContract
from synamic.core.functions.decorators import loaded, not_loaded


class Static(ContentContract):
    def __init__(self, config, module, path):
        self.__url = None
        self.__config = config
        self.__module = module
        self.__path = path

    def set_url_obj(self, url_obj):
        assert self.__url is None, "Cannot set url object twice"
        self.__url = url_obj

    @property
    def module(self):
        return self.__module

    @property
    def path(self):
        return self.__path


    def get_stream(self):
        file = open(self.path.absolute_path, 'rb')
        return file

    @property
    def content_type(self):
        mime_type = 'octet/stream'
        path = self.__url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type


class Statics(ContentModuleContract):

    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False

    @property
    def generic_name(self):
        return 'content'

    @property
    def extensions(self):
        return None

    @property
    def name(self):
        return 'statics'

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_paths(self)
        for file_path in paths:
            print("File path is: ", file_path.relative_path)
            print("Is file: ", file_path.is_file)
            static = Static(self.__config, self, file_path)
            url = Url(self.__config, static, (self.root_path + file_path.relative_path), None, False)
            static.set_url_obj(url)
            self.__config.add_url(url)
        # Add static files
        self.__is_loaded = True

    @property
    def dependencies(self):
        return set()

    @property
    def directory_name(self):
        return 'static'

    @property
    def parent_dir(self):
        return self.__config.content_dir

    @property
    def dotted_path(self):
        return 'synamic.content_modules.statics.Statics'

    @property
    def root_path(self):
        return ''
