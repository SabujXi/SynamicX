from synamic.core.services.content.functions.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import Syd


class ObjectManager:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__is_loaded = False
        self.__content_metas = {}

    #  @loaded
    def reload(self):
        self.__is_loaded = False
        self.__content_metas.clear()
        self.load()

    @property
    def is_loaded(self):
        return self.__is_loaded

    #  @not_loaded
    def load(self):
        self.__cache_content_metas()

        self.__is_loaded = True

    def __cache_content_metas(self):
        if self.__synamic.env['backend'] == 'file':  # TODO: fix it.
            path_tree = self.get_path_tree()
            content_dir = self.__synamic.default_configs.get('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_paths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    content_meta = Syd(front_matter)
                    self.__content_metas[file_path.path_components] = content_meta
                else:
                    self.__synamic.add_static_content(file_path)
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented
        self.__is_loaded = True

    #  @loaded
    def get_content_meta(self, path):
        path_tree = self.__synamic.get_service('path_tree')
        path = path_tree.create_path(path)
        if self.__synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__content_metas[path.path_components]

    #  @loaded
    def get_content(self, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        pass

    def get_static_file_paths(self):
        pass

    @staticmethod
    def empty_syd():
        return Syd('')

    def get_raw_data(self, path) -> str:
        path = self.get_path_tree().create_file_path(path)
        with path.open('r', encoding='utf-8') as f:
            text = f.read()
        return text

    def get_syd(self, path) -> Syd:
        syd = Syd(self.get_raw_data(path))
        return syd

    def get_model(self, model_name):
        model_dir = self.__synamic.default_configs.get('metas.models')
        path_tree = self.__synamic.get_service('path_tree')
        path = path_tree.create_file_path(model_dir, model_name + '.model')
        model_text = self.get_raw_data(path)
        return ModelParser.parse(model_name, model_text)

    def get_content_parts(self, content_path):
        text = self.get_raw_data(content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = Syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body


    def get_path_tree(self):
        path_tree = self.__synamic.get_service('path_tree')
        return path_tree

    def get_url(self, url_str):
        url_str = url_str.strip()
        low_url = url_str.lower()
        if low_url.startswith('http://') or low_url.startswith('https://') or low_url.startswith('ftp://'):
            return url_str
        elif low_url.startswith('geturl://'):
            new_url = url_str[len('geturl://'):]
        else:
            new_url = url_str

    def get_site_settings(self):
        return self.__synamic.get_service('site_settings').make_site_settings()

    def get_content_by_segments(self, site_id, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

