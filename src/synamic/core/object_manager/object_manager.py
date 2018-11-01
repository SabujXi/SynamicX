from collections import defaultdict
from synamic.core.services.content.functions.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import Syd
from ._content_manager import ContentObjectManager
from . _marker_manager import MarkerObjectManager
from ._model_manager import ModelObjectManager


class ObjectManager(
        ContentObjectManager,
        MarkerObjectManager,
        ModelObjectManager):
    def __init__(self, site):
        self.__site = site

        # content
        self.__content_metas_cachemap = {}

        # marker
        self.__marker_by_id_cachemap = {}

        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def site(self):
        return self.__site

    #  @loaded
    def reload(self):
        self.__is_loaded = False
        self.__content_metas_cachemap.clear()
        self.__marker_by_id_cachemap.clear()
        self.load()

    #  @not_loaded
    def load(self):
        self.__cache_markers()
        self.__cache_content_metas()
        self.__is_loaded = True

    def __cache_content_metas(self):
        if self.__site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = self.__site.get_service('contents')
            path_tree = self.get_path_tree()
            content_dir = self.__site.synamic.default_configs.get('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_cpaths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    fields_syd = self.make_syd(front_matter)
                    content_meta = content_service.make_content_fields(fields_syd, file_path)
                    self.__content_metas_cachemap[file_path.id] = content_meta
                else:
                    self.__site.synamic.add_static_content(file_path)  # TODO
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented
        self.__is_loaded = True

    def __cache_markers(self):
        if len(self.__marker_by_id_cachemap) == 0:
            marker_service = self.__site.get_service('markers')
            marker_ids = marker_service.get_marker_ids()
            print("marker_ids: %s" % str(marker_ids))
            for marker_id in marker_ids:
                marker = marker_service.make_marker(marker_id)
                self.__marker_by_id_cachemap[marker_id] = marker

    #  @loaded
    def get_content_meta(self, path):
        path_tree = self.__site.get_service('path_tree')
        path = path_tree.create_cpath(path)
        if self.__site.synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__content_metas_cachemap[path.path_comps]

    #  @loaded
    def get_content(self, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents except md contents.
        content_service = self.__site.get_service('contents')
        path_tree = self.get_path_tree()
        contents_dir = self.__site.default_configs.get('dirs')['contents.contents']
        file_cpath = path_tree.create_file_cpath(contents_dir + '/' + path)
        md_content = content_service.make_md_content(file_cpath)
        return md_content

    def get_static_file_paths(self):
        pass

    def all_static_paths(self):
        paths = []
        path_tree = self.__site.get_service('path_tree')
        statics_dir = self.__site.default_configs.get('dirs')['statics.statics']
        contents_dir = self.__site.default_configs.get('dirs')['contents.contents']
        paths.extend(path_tree.list_file_cpaths(statics_dir))

        for path in path_tree.list_file_cpaths(contents_dir):
            if path.basename.lower().endswith(('.md', '.markdown')):
                paths.append(path)
        return paths

    @staticmethod
    def empty_syd():
        return Syd('')

    def get_raw_data(self, path) -> str:
        path = self.get_path_tree().create_file_cpath(path)
        with path.open('r', encoding='utf-8') as f:
            text = f.read()
        return text

    def get_syd(self, path) -> Syd:
        syd = Syd(self.get_raw_data(path)).parse()
        return syd

    def make_syd(self, raw_data):
        syd = Syd(raw_data).parse()
        return syd

    def get_model(self, model_name):
        model_dir = self.__site.synamic.default_configs.get('dirs')['metas.models']
        path_tree = self.__site.get_service('path_tree')
        path = path_tree.create_file_cpath(model_dir, model_name + '.model')
        model_text = self.get_raw_data(path)
        return ModelParser.parse(model_name, model_text)

    def get_content_parts(self, content_path):
        text = self.get_raw_data(content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self):
        path_tree = self.__site.get_service('path_tree')
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
        return self.__site.get_service('site_settings').make_site_settings()

    def get_content_by_segments(self, site_id, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

    def get_marker(self, marker_id):
        if marker_id in self.__marker_by_id_cachemap:
            return self.__marker_by_id_cachemap[marker_id]
        else:
            raise Exception('Marker does not exist: %s' % marker_id)

    def get_markers(self, marker_type):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        _ = []
        for marker in self.__marker_by_id_cachemap.values():
            if marker.type == marker_type:
                _.append(marker)
        return _

    @property
    def cached_content_metas(self):  # TODO: logic for cached content metas - when to use it when not (when not cached)
        return self.__content_metas_cachemap.copy()

