import mimetypes
from synamic.core.classes.url import ContentUrl
from synamic.core.contracts import BaseContentModuleContract
from synamic.core.contracts.document import StaticDocumentContract
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.functions.normalizers import normalize_key, normalize_relative_file_path, normalize_content_url_path
from synamic.core.classes.mapping import FinalizableDict
from synamic.core.classes.static import StaticContent


class StaticModule(BaseContentModuleContract):
    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False

    @property
    def name(self):
        return 'static'

    @property
    def content_class(self):
        return StaticContent

    @property
    def config(self):
        return self.__config

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_file_paths(self)
        for file_path in paths:
            print("File path relative is: ", file_path.relative_path)
            assert file_path.is_file  # Remove in prod
            self.__config.add_static_content(file_path, self.name)
        self.__is_loaded = True

    @property
    def dependencies(self):
        return set()

    @property
    def root_url_path(self):
        return ''