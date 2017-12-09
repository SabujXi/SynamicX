import mimetypes
from synamic.core.classes.url import ContentUrl
from synamic.core.contracts import ContentModuleContract
from synamic.core.contracts.document import StaticDocumentContract
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.functions.normalizers import normalize_key, normalize_relative_file_path, normalize_content_url_path


class StaticContent(StaticDocumentContract):
    def __init__(self, config, module, path):
        self.__url = None
        self.__config = config
        self.__module = module
        self.__path = path

        self.__content_id = None
        self.__content_name = None

    # def set_url_obj(self, url_obj):
    #     assert self.__url is None, "Cannot set url_object object twice"
    #     self.__url = url_obj

    @property
    def module_object(self):
        return self.__module

    @property
    def path_object(self):
        return self.__path

    @property
    def content_id(self):
        return self.__content_id
        # return self.module_object.name + ":" + self.path_object.relative_path  # Should be more intelligent? Ok, let's think about that later.

    @content_id.setter
    def content_id(self, cid):
        assert self.__content_id is None, 'No repeat please'
        self.__content_id = cid

    def get_stream(self):
        file = self.__config.path_tree.open_file(self.path_object.relative_path, 'rb')
        return file

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.__url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def absolute_path(self):
        raise NotImplemented

    @property
    def content_type(self):
        return self.types.STATIC

    @property
    def content_name(self):
        # raise NotImplemented
        return self.__content_name

    @content_name.setter
    def content_name(self, name):
        assert self.__content_name is None, 'No repeat please'
        self.__content_name = name

    @property
    def url_object(self):
        return self.__url

    @url_object.setter
    def url_object(self, url_object):
        assert self.__url is None
        self.__url = url_object


class StaticModule(ContentModuleContract):

    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False

    @property
    def extensions(self):
        return None

    @property
    def name(self):
        return normalize_key('static')

    @property
    def content_class(self):
        return StaticContent

    @property
    def config(self):
        return self.__config

    @property
    def is_loaded(self):
        return self.__is_loaded

    def set_url_and_content_info(self, file_path, static_content):
        if file_path.meta_info:
            permalink = file_path.meta_info.get(normalize_key('permalink'), None)
            if permalink:
                permalink = permalink.rstrip(r'\/')
            id = file_path.meta_info.get(normalize_key('id'), None)
            if id:
                static_content.content_id = id
            name = file_path.meta_info.get(normalize_key('name'), None)
            if name:
                static_content.content_name = name

            if permalink:
                cnt_url = ContentUrl(self.__config, permalink, is_dir=False)
            else:
                cnt_url = ContentUrl(self.__config, normalize_relative_file_path(file_path.relative_path),
                                 is_dir=False)
        else:
            cnt_url = ContentUrl(self.__config, (self.root_url_path + file_path.listing_relative_path.replace('\\', '/')),
                             False)
        static_content.url_object = cnt_url

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_paths(self)
        for file_path in paths:
            print("File path relative is: ", file_path.relative_path)
            assert file_path.is_file  # Remove in prod
            static = StaticContent(self.__config, self, file_path)
            self.set_url_and_content_info(file_path, static)
            print("Static URL Path: %s" % static.url_object.path)
            self.__config.add_document(static)
        # Add static files
        self.__is_loaded = True

    @property
    def dependencies(self):
        return set()

    @property
    def root_url_path(self):
        return ''

    def enqueue_file(self, mod_obj, path):
        static_content = StaticContent(self.__config, mod_obj, path)
        self.set_url_and_content_info(path, static_content)
        self.__config.add_document(static_content)

