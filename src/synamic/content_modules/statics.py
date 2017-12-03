import mimetypes
from synamic.core.classes.url import ContentUrl
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

    @property
    def content_id(self):
        return self.module.name + ":" + self.path.relative_path  # Should be more intelligent? Ok, let's think about that later.

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

    @property
    def is_static(self):
        return True

    @property
    def is_auxiliary(self):
        return False

    @property
    def is_dynamic(self):
        return False



class Statics(ContentModuleContract):

    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False


    @property
    def extensions(self):
        return None

    @property
    def name(self):
        return 'static'

    @property
    def content_class(self):
        return Static

    @property
    def config(self):
        return self.__config

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_paths(self)
        for file_path in paths:
            print("File path relative is: ", file_path.relative_path)
            print("File path root relative is: ", file_path.relative_path_from_root)
            assert file_path.is_file  # Remove in prod
            static = Static(self.__config, self, file_path)
            url = ContentUrl(self.__config, static, (self.root_url_path + file_path.relative_path_from_module_root), None, False)
            print("URL: %s" % url.path)
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
    def root_url_path(self):
        return ''
