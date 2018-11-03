from collections import defaultdict, OrderedDict
from synamic.core.contracts import DocumentType
from synamic.core.services.content.functions.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.standalones.functions.decorators import loaded, not_loaded


class ObjectManager:
    def __init__(self, synamic):
        self.__site_object_managers = OrderedDict({})

        self.__synamic = synamic

        # content
        self.__content_fields_cachemap = defaultdict(dict)

        # marker
        self.__marker_by_id_cachemap = defaultdict(dict)

        # site settings
        self.__site_settings_cachemap = defaultdict(dict)

        # url object to contents
        self.__url_to_text_content_paths_cachemap = defaultdict(dict)

        # syd cachemap
        self.__cpath_to_syd_cachemap = defaultdict(dict)

        self.__is_loaded = False

    def get_manager_for_site(self, site):
        if site.id not in self.__site_object_managers:
            om_4_site = self.__ObjectManagerForSite(site, self)
            self.__site_object_managers[site.id] = om_4_site
        else:
            om_4_site = self.__site_object_managers[site.id]
        return om_4_site

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    def _reload_for(self, site):
        self.__content_fields_cachemap[site.id].clear()
        self.__marker_by_id_cachemap[site.id].clear()
        self.__url_to_text_content_paths_cachemap[site.id].clear()
        self._load_for(site)

    def _load_for(self, site):
        self.__cache_markers(site)
        self.__cache_content_metas(site)
        self.__cache_urls(site)

    def __cache_content_metas(self, site):
        if site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = site.get_service('contents')
            path_tree = self.get_path_tree(site)
            content_dir = site.synamic.default_configs.get('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_cpaths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(site, file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    fields_syd = self.make_syd(front_matter)
                    content_meta = content_service.make_content_fields(fields_syd, file_path)
                    self.__content_fields_cachemap[site.id][file_path.id] = content_meta
                else:
                    # No need to cache anything about static file.
                    pass
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented

    def __cache_markers(self, site):
        if len(self.__marker_by_id_cachemap[site.id]) == 0:
            marker_service = site.get_service('markers')
            marker_ids = marker_service.get_marker_ids()
            for marker_id in marker_ids:
                marker = marker_service.make_marker(marker_id)
                self.__marker_by_id_cachemap[site.id][marker_id] = marker

    def __cache_urls(self, site):
        if len(self.__url_to_text_content_paths_cachemap[site.id]) == 0:
            for content_fields in self.__content_fields_cachemap[site.id].values():
                # TODO: convert permalink to path and slug along with dir based url
                path = content_fields.get('path', None)
                slug = content_fields.get('slug', None)
                permalink = content_fields.get('permalink', None)  # Temporarily keeping it for backward compatibility.
                                                                   # TODO: remove it and keep path only
                if permalink is not None:
                    path = permalink

                if path is not None:
                    #  discard everything and keep it. No processing needed.
                    pass
                elif slug is not None:
                    # calculate through file system.
                    cpath = content_fields.get_content_path()
                    cpath_comps = cpath.path_comps
                    basename = cpath_comps[-1]
                    cpath_comps = cpath_comps[1:-1]  # ignoring `contents` dir  TODO: make it more logical and dynamic
                    # instead of hard coded.
                    _ = []
                    for ccomp in cpath_comps:
                        if not ccomp.startswith('_'):
                            _.append(ccomp)

                    cpath_comps = _
                    cpath_comps.append(slug)
                    path = cpath_comps
                else:
                    # calculate through file system.
                    cpath = content_fields.get_content_path()
                    cpath_comps = cpath.path_comps
                    basename = cpath_comps[-1]
                    cpath_comps = cpath_comps[1:-1]  # ignoring `contents` dir  TODO: make it more logical and dynamic
                    # instead of hard coded.
                    _ = []
                    for ccomp in cpath_comps:
                        if not ccomp.startswith('_'):
                            _.append(ccomp)

                    cpath_comps = _
                    cpath_comps.append(basename)
                    path = cpath_comps

                url_path_comps = path
                url_object = self.__synamic.router.make_url(
                    site,
                    url_path_comps,
                    for_document_type=content_fields.get_document_type()
                )
                print(url_object)
                self.__url_to_text_content_paths_cachemap[site.id][url_object] = content_fields.get_content_path()

    #  @loaded
    def get_content_meta(self, site, path):
        path_tree = site.get_service('path_tree')
        path = path_tree.create_cpath(path)
        if site.synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__content_fields_cachemap[site.id][path.path_comps]

    #  @loaded
    def get_text_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents besides md contents.
        content_service = site.get_service('contents')
        path_tree = self.get_path_tree(site)
        contents_dir = site.default_configs.get('dirs')['contents.contents']
        if isinstance(path, str):
            file_cpath = path_tree.create_file_cpath(contents_dir + '/' + path)
        else:
            file_cpath = path
        md_content = content_service.make_md_content(file_cpath)
        return md_content

    def get_binary_content(self, site, path):
        path_tree = site.get_service('path_tree')
        if not path_tree.exists(path):
            return None
        else:
            content_service = site.get_service('contents')
            return content_service.make_static_content(path)

    def get_static_file_paths(self, site):
        pass

    def all_static_paths(self, site):
        paths = []
        path_tree = site.get_service('path_tree')
        statics_dir = site.default_configs.get('dirs')['contents.statics']
        contents_dir = site.default_configs.get('dirs')['contents.contents']
        paths.extend(path_tree.list_file_cpaths(statics_dir))

        for path in path_tree.list_file_cpaths(contents_dir):
            if path.basename.lower().endswith(('.md', '.markdown')):
                paths.append(path)
        return paths

    @staticmethod
    def empty_syd():
        return SydParser('').parse()

    def get_raw_data(self, site, path) -> str:
        path_tree = self.get_path_tree(site)
        if not path_tree.is_cpath_type(path):
            path = path_tree.create_file_cpath(path)
        with path.open('r', encoding='utf-8') as f:
            text = f.read()
        return text

    def get_syd(self, site, path):
        path_tree = self.get_path_tree(site)
        if not path_tree.is_cpath_type(path):
            path = path_tree.create_file_cpath(path)

        if path in self.__cpath_to_syd_cachemap:
            syd = self.__cpath_to_syd_cachemap[path]
        else:
            syd = SydParser(self.get_raw_data(site, path)).parse()
            self.__cpath_to_syd_cachemap[path] = syd
        return syd

    def make_syd(self, raw_data):
        syd = SydParser(raw_data).parse()
        return syd

    def get_model(self, site, model_name):
        model_dir = site.synamic.default_configs.get('dirs')['metas.models']
        path_tree = site.get_service('path_tree')
        path = path_tree.create_file_cpath(model_dir, model_name + '.model')
        model_text = self.get_raw_data(site, path)
        return ModelParser.parse(model_name, model_text)

    def get_content_parts(self, site, content_path):
        text = self.get_raw_data(site, content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self, site):
        path_tree = site.get_service('path_tree')
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

    def get_site_settings(self, site):
        ss = self.__site_settings_cachemap.get(site.id, None)
        if ss is None:
            ss = site.get_service('site_settings').make_site_settings()
            self.__site_settings_cachemap[site.id] = ss
        return ss

    def get_content_by_segments(self, site, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

    def get_marker(self, site, marker_id):
        if marker_id in self.__marker_by_id_cachemap[site.id]:
            return self.__marker_by_id_cachemap[site.id][marker_id]
        else:
            raise Exception('Marker does not exist: %s' % marker_id)

    def get_markers(self, site, marker_type):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        _ = []
        for marker in self.__marker_by_id_cachemap[site.id].values():
            if marker.type == marker_type:
                _.append(marker)
        return _

    def get_cached_content_metas(self, site):
        # TODO: logic for cached content metas
        # - when to use it when not (when not cached)
        return self.__content_fields_cachemap[site].copy()

    def get_text_cpath_by_curl(self, site, url_object, default=None):
        content_cpath = self.__url_to_text_content_paths_cachemap[site.id].get(url_object, default)
        return content_cpath

    class __ObjectManagerForSite:
        def __init__(self, site, object_manager):
            self.__site = site
            self.__object_manager = object_manager
            self.__is_loaded = False

        @property
        def is_loaded(self):
            return self.__is_loaded

        @loaded
        def reload(self):
            self.__is_loaded = False
            self.__object_manager._reload_for(self.site)
            self.__is_loaded = True

        @not_loaded
        def load(self):
            self.__object_manager._load_for(self.site)
            self.__is_loaded = True

        @property
        def site(self):
            return self.__site

        def get_content_meta(self, path):
            return self.__object_manager.get_content_meta(self.site, path)

        def get_text_content(self, path):
            return self.__object_manager.get_text_content(self.site, path)

        def get_binary_content(self, path):
            return self.__object_manager.get_binary_content(self.site, path)

        def get_static_file_paths(self):
            return self.__object_manager.get_static_file_paths(self.site)

        def all_static_paths(self):
            self.__object_manager.all_static_paths(self.site)

        def empty_syd(self):
            return self.__object_manager.empty_syd()

        def get_raw_data(self, path) -> str:
            return self.__object_manager.get_raw_data(self.site, path)

        def get_syd(self, path):
            return self.__object_manager.get_syd(self.site, path)

        def make_syd(self, raw_data):
            return self.__object_manager.make_syd(raw_data)

        def get_model(self, model_name):
            return self.__object_manager.get_model(self.site, model_name)

        def get_content_parts(self, content_path):
            return self.__object_manager.get_content_parts(self.site, content_path)

        def get_path_tree(self):
            return self.__object_manager.get_path_tree(self.site)

        def get_url(self, url_str):
            return self.__object_manager.get_url(self.site, url_str)

        def get_site_settings(self):
            return self.__object_manager.get_site_settings(self.site)

        def get_content_by_segments(self, path_segments, pagination_segments):
            return self.__object_manager.get_content_by_segments(self.site, path_segments, pagination_segments)

        def get_marker(self, marker_id):
            return self.__object_manager.get_marker(self.site, marker_id)

        def get_markers(self, marker_type):
            return self.__object_manager.get_markers(self.site, marker_type)

        @property
        def cached_content_metas(self):
            return self.__object_manager.get_cached_content_metas(self.site)

        def get_text_cpath_by_curl(self, url_object, default=None):
            return self.__object_manager.get_text_cpath_by_curl(self.site, url_object, default=None)

