import types
from collections import defaultdict, OrderedDict
from synamic.core.services.content.content_splitter import content_splitter
from synamic.core.parsing_systems.model_parser import ModelParser
from synamic.core.parsing_systems.curlybrace_parser import SydParser
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.contracts import CDocType
from .query import QueryNode, SimpleQueryParser
from synamic.core.services.content.paginated_content import PaginationPage


class ObjectManager:
    def __init__(self, synamic):
        self.__synamic = synamic

        self.__site_object_managers = OrderedDict({})
        self.__site_settings = defaultdict(dict)

        self.__cache = self.__Cache(self.__synamic)

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
        self.__cache.clear_cache(site)
        self._load_for(site)

    def _load_for(self, site):
        self.__cache_markers(site)
        self.__cache_marked_cfields(site)
        self.__cache_pre_processed_contents(site)
        self.__cache_menus(site)

    def __cache_marked_cfields(self, site):
        if site.synamic.env['backend'] == 'file':  # TODO: fix it.
            content_service = site.get_service('contents')
            path_tree = self.get_path_tree(site)
            content_dir = site.synamic.default_data.get_syd('dirs')['contents.contents']

            # for content
            file_paths = path_tree.list_file_cpaths(content_dir)
            for file_path in file_paths:
                if file_path.extension.lower() in {'md', 'markdown'}:
                    text = self.get_raw_data(site, file_path)
                    front_matter, body = content_splitter(file_path, text)
                    del body
                    fields_syd = self.make_syd(front_matter)
                    cfields = content_service.build_cfields(fields_syd, file_path)
                    self.__cache.add_marked_cfields(site, cfields)
                else:
                    # No need to cache anything about static file.
                    pass
        else:
            raise NotImplemented
            # database backend is not implemented yet. AND there is nothing to do here for db, skip it when implemented

    def __cache_markers(self, site):
        marker_service = site.get_service('markers')
        marker_ids = marker_service.get_marker_ids()
        for marker_id in marker_ids:
            marker = marker_service.make_marker(marker_id)
            self.__cache.add_marker(site, marker_id, marker)
            # self.__marker_by_id_cachemap[site.id][marker_id] = marker

    def __cache_pre_processed_contents(self, site):
        pre_processor_service = site.get_service('pre_processor')
        pre_processors = pre_processor_service.pre_processors
        for pre_processor in pre_processors:
            generated_contents = pre_processor.get_generated_contents()
            for generated_content in generated_contents:
                self.__cache.add_pre_processed_content(site, generated_content, generated_content.source_cpath)
                # self.__pre_processed_content_cachemap[site.id][generated_content.id] = generated_content

    def __cache_menus(self, site):
        menu_service = site.get_service('menus')
        menu_names = menu_service.get_menu_names()
        for menu_name in menu_names:
            menu = menu_service.make_menu(menu_name)
            self.__cache.add_menu(site, menu_name, menu)

    def make_url_for_marked_content(self, site, file_cpath, path=None, slug=None, for_cdoctype=CDocType.TEXT_DOCUMENT):
        if path is not None:
            #  discard everything and keep it. No processing needed.
            pass
        elif slug is not None:
            # calculate through file system.
            cpath_comps = file_cpath.path_comps
            basename = cpath_comps[-1]
            # TODO: what to do to basename? unused!
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
            cpath_comps = file_cpath.path_comps
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
        curl = self.__synamic.router.make_url(
            site,
            url_path_comps,
            for_cdoctype=for_cdoctype
        )
        return curl

    def static_content_cpath_to_url(self, site, cpath, for_cdoctype):
        assert CDocType.is_binary(for_cdoctype, not_generated=True)
        # For STATIC Files
        curl = self.__synamic.router.make_url(
            site,
            cpath.path_comps,
            for_cdoctype=for_cdoctype
        )
        return curl

    #  @loaded
    def get_cfields(self, site, path, default=None):
        path_tree = site.get_service('path_tree')
        path = path_tree.create_cpath(path)
        if site.synamic.env['backend'] == 'database':
            raise NotImplemented
        else:
            # file backend
            return self.__cache.get_marked_cfields_by_cpath(site, path, default=default)

    #  @loaded
    def get_marked_content(self, site, path):
        # create content, meta, set meta with converters. Setting it from here will help caching.
        # TODO: other type of contents besides md contents.
        content_service = site.get_service('contents')
        if isinstance(path, str):
            path_tree = self.get_path_tree(site)
            contents_cdir = path_tree.create_dir_cpath(site.default_data.get_syd('dirs')['contents.contents'])
            file_cpath = contents_cdir.join(path, is_file=True)
        else:
            file_cpath = path

        # check cache
        marked_content = self.__cache.get_marked_content_by_cpath(site, file_cpath, None)
        if marked_content is not None:
            return marked_content

        if not file_cpath.exists():
            return None
        else:
            cached_cfields = self.__cache.get_marked_cfields_by_cpath(site, file_cpath)
            assert cached_cfields is not None
            marked_content = content_service.build_md_content(file_cpath, cached_cfields)
            # cache it.
            self.__cache.add_marked_content(site, marked_content)
            return marked_content

    def get_marked_content_by_url(self, site, curl):
        cpath = self.__cache.get_marked_cpath_by_curl(site, curl)
        return self.get_marked_content(site, cpath)

    def get_marked_contents_by_cpaths(self, site, cpaths):
        contents = []
        for cpath in cpaths:
            contents.append(self.get_marked_content(site, cpath))
        return contents

    def get_binary_content(self, site, path):
        path_tree = site.get_service('path_tree')
        if not path_tree.exists(path):
            return None
        else:
            content_service = site.get_service('contents')
            return content_service.build_static_content(path)

    def get_static_file_paths(self, site):
        paths = []
        path_tree = site.get_service('path_tree')
        statics_dir = site.default_data.get_syd('dirs')['contents.statics']
        contents_dir = site.default_data.get_syd('dirs')['contents.contents']
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
        if not path_tree.is_type_cpath(path):
            path = path_tree.create_file_cpath(path)
        with path.open('r', encoding='utf-8') as f:
            text = f.read()
        return text

    def get_syd(self, site, path):
        path_tree = self.get_path_tree(site)
        if not path_tree.is_type_cpath(path):
            path = path_tree.create_file_cpath(path)

        syd = self.__cache.get_syd(site, path, default=None)
        if syd is None:
            syd = SydParser(self.get_raw_data(site, path)).parse()
            self.__cache.add_syd(site, path, syd)
        return syd

    @staticmethod
    def make_syd(raw_data):
        syd = SydParser(raw_data).parse()
        return syd

    def get_model(self, site, model_name):
        """Nothing from the system model be overridden - this is opposite of system syd to user settings."""
        types = site.get_service('types')

        model_dir = site.synamic.default_data.get_syd('dirs')['metas.models']
        path_tree = site.get_service('path_tree')
        user_model_cpath = path_tree.create_file_cpath(model_dir, model_name + '.model')

        processed_model = self.__cache.get_model(site, model_name, None)
        if processed_model is None:
            system_model = site.default_data.get_model(model_name, None)
            if system_model is None:
                user_model = ModelParser.parse(model_name, self.get_raw_data(site, user_model_cpath))
                new_model = user_model
            else:
                user_model = ModelParser.parse(model_name, self.get_raw_data(site, user_model_cpath))
                new_model = user_model.new(system_model)
            # put converters inside of the cfields
            for key, field in new_model.items():
                converter = types.get_converter(field.converter_name)
                field.set_converter(converter)
            self.__cache.add_model(site, new_model)
            return new_model
        else:
            return processed_model

    def get_content_parts(self, site, content_path):
        text = self.get_raw_data(site, content_path)
        front_matter, body = content_splitter(content_path, text)
        front_matter_syd = self.make_syd(front_matter)  # Or take it from cache.
        return front_matter_syd, body

    def get_path_tree(self, site):
        return site.get_service('path_tree')

    @staticmethod
    def __get_with_x_scheme(url_str):
        url_str = url_str.strip()
        low_url = url_str.lower()
        if '://' in low_url:
            scheme, url_content = url_str.split('://', 1)
        else:
            scheme = None
            url_content = url_str

        if scheme is not None:
            if scheme.lower() not in ('geturl', 'getfields', 'getcontent'):
                ordinary_url = True
            else:
                scheme = scheme.lower()
                ordinary_url = False
        else:
            ordinary_url = True

        return ordinary_url, scheme, url_content

    def getfields(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str

        result_cfields = None
        fields_for, for_value = url_content.split(':')
        assert fields_for in ('file', 'id')
        if fields_for == 'file':
            file_cpath = site.get_service('path_tree').create_file_cpath(for_value)
            marked_cfields = self.__cache.get_marked_cfields_by_cpath(site, file_cpath, None)
            if marked_cfields is not None:
                result_cfields = marked_cfields

        elif fields_for == 'id':
            for marked_cfields in self.__cache.get_all_marked_cfields(site):
                if marked_cfields.id == for_value:
                    result_cfields = marked_cfields
                    break
        else:  # content
            raise NotImplemented

        if result_cfields is None:
            raise Exception('Fields not found for getfields(): %s' % url_str)
        else:
            return result_cfields

    def getcontent(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str
        result_content = self.get_marked_content(site, self.getfields(site, url_str).cpath)
        return result_content

    def geturl(self, site, url_str):
        ordinary_url, scheme, url_content = self.__get_with_x_scheme(url_str)
        if ordinary_url:
            return url_str

        result_url = None
        url_for, for_value = url_content.split(':')
        assert url_for in ('file', 'sass', 'id')
        if url_for == 'file':
            file_cpath = site.get_service('path_tree').create_file_cpath(for_value)
            marked_cfields = self.__cache.get_marked_cfields_by_cpath(site, file_cpath, None)
            if marked_cfields is not None:
                result_url = marked_cfields.curl
            else:
                # try STATIC
                result_url = self.static_content_cpath_to_url(site, file_cpath, CDocType.BINARY_DOCUMENT)
        elif url_for == 'sass':
            # pre-processor stuff. Must be in pre processed content.
            scss_cpath = site.get_service('pre_processor').get_processor('sass').make_cpath(for_value)
            scss_content = self.__cache.get_pre_processed_content_by_cpath(site, scss_cpath, None)
            if scss_content is not None:
                result_url = scss_content.curl
        elif url_for == 'id':
            for cfields in self.__cache.get_all_marked_cfields(site):
                if cfields.id == for_value:
                    result_url = cfields.curl
                    break
        else:  # content
            raise NotImplemented

        if result_url is None:
            raise Exception('URL not found for geturl(): %s' % url_str)
        else:
            return result_url.url_encoded

    def get_site_settings(self, site):
        ss = self.__site_settings.get(site.id, None)
        if ss is None:
            ss = site.get_service('site_settings').make_site_settings()
            self.__site_settings[site.id] = ss
        return ss

    def get_content_by_segments(self, site, path_segments, pagination_segments):
        """Method primarily for router.get()"""
        pass

    def get_marker(self, site, marker_id):
        marker = self.__cache.get_marker(site, marker_id, default=None)
        if marker is None:
            raise Exception('Marker does not exist: %s' % marker_id)
        return marker

    def get_markers(self, site, marker_type):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        _ = []
        for marker in self.__cache.get_markers(site):
            if marker.type == marker_type:
                _.append(marker)
        return _

    def get_all_cached_marked_fields(self, site):
        # TODO: logic for cached content metas
        # - when to use it when not (when not cached)
        return self.__cache.get_all_marked_cfields(site)

    def get_marked_cpath_by_curl(self, site, curl, default=None):
        return self.__cache.get_marked_cpath_by_curl(site, curl, default=default)

    def get_menu(self, site, menu_name, default=None):
        return self.__cache.get_menu(site, menu_name, default=default)

    @staticmethod
    def __convert_section_value(section, content_model):
        # TODO: for converter that returns single value implement mechanism that will help use in !in for them.
        converted_value = content_model[section.key].converter(section.value)
        return SimpleQueryParser.QuerySection(key=section.key, comp_op=section.comp_op, value=converted_value)

    def __query_cfields_left_right(self, section, result_set, content_model):
        matched_result = set()
        for cfields in result_set:
            field_value = cfields.get(section.key, None)
            converter = content_model[section.key].converter
            if field_value is not None:
                if converter.compare(section.comp_op, field_value, section.value):
                    matched_result.add(cfields)
            else:
                if section.comp_op in ('!=', '!in'):
                    matched_result.add(cfields)
        return matched_result

    def __query_cfields_by_node(self, node, result_set, content_model):
        if isinstance(node, SimpleQueryParser.QuerySection):
            # only one section here.
            left_section = node
            right_section = None
            logic_op = None
        else:
            assert isinstance(node, QueryNode)
            logic_op = node.logic_op
            if isinstance(node.left, QueryNode):
                return self.__query_cfields_by_node(node.left, result_set, content_model)
            else:
                left_section = node.left
                right_section = None

            if isinstance(node.right, QueryNode):
                return self.__query_cfields_by_node(node.left, result_set, content_model)
            else:
                right_section = node.right

        left_section = self.__convert_section_value(left_section, content_model)
        left_result = self.__query_cfields_left_right(left_section, result_set, content_model)
        if right_section is not None:
            right_section = self.__convert_section_value(right_section, content_model)
            right_result = self.__query_cfields_left_right(right_section, result_set, content_model)
        else:
            right_result = None

        if logic_op == '|':
            left_result.update(right_result)
        elif logic_op == '&':
            left_result.intersection_update(right_result)
        else:
            # keep as is
            pass
        result_set.clear()
        result_set.update(left_result)
        return result_set

    def query_cfields(self, site, query_str):
        content_model = site.object_manager.get_model('content')
        node, sort = SimpleQueryParser(query_str).parse()
        all_cfields_s = self.__cache.get_all_marked_cfields(site)
        result = set(all_cfields_s)
        if node is not None:
            self.__query_cfields_by_node(node, result, content_model)
        if sort is not None:
            def sorting_key_func(f):
                value = f[sort.by_key]
                return value
            result = sorted(
                result,
                key=sorting_key_func,
                reverse=True if sort.order == 'desc' else False
            )

        return tuple(result)

    def query_contents(self, site, query_str):
        cfields_s = self.query_cfields(site, query_str)
        _ = []
        for cfields in cfields_s:
            _.append(
                self.get_marked_content(site, cfields.cpath)
            )
        return tuple(_)

    def get_user(self, site, user_id):
        user = self.__cache.get_user(site, user_id, None)
        if user is None:
            user_service = site.get_service('users')
            user = user_service.make_user(user_id)
            self.__cache.add_user(site, user)
        return user

    class __ObjectManagerForSite:
        def __init__(self, site, object_manager):
            self.__site = site
            self.__object_manager = object_manager
            self.__is_loaded = False

            # real object manager methods.
            self.__cached_om_methods = {}

        def __getattr__(self, key):
            res = self.__cached_om_methods.get(key, None)
            if res is None:
                attr = getattr(self.__object_manager, key)
                if not isinstance(attr, types.MethodType):  # or key.startswith('_')
                    res = attr
                else:
                    om_method = attr

                    def call_om_method(*args, **kwargs):
                        return om_method(self.__site, *args, **kwargs)
                    self.__cached_om_methods[key] = call_om_method
                    res = call_om_method
            return res

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

    class __Cache:
        def __init__(self, synamic):
            self.__synamic = synamic

            # marker
            self.__marker_by_id_cachemap = defaultdict(dict)
            # syd cachemap
            self.__cpath_to_syd_cachemap = defaultdict(dict)

            # menus
            self.__menus_cachemap = defaultdict(dict)

            # models
            self.__models_cachemap = defaultdict(dict)

            # users
            self.__users_cachemap = defaultdict(dict)

            # >>>>>>>>
            # CONTENTS
            self.__pre_processed_cachemap = defaultdict(dict)  # curl to content
            self.__marked_contents_cachemap = defaultdict(dict)  # curl to content: default limit 100 per site. < limit not yet implemented
            self.__marked_cfields_cachemap = defaultdict(dict)  # curl to content

            self.__cpath_to_pre_processed_contents = defaultdict(dict)
            self.__cpath_to_marked_content = defaultdict(dict)
            self.__cpath_to_marked_cfields = defaultdict(dict)
            # <<<<<<<<

        def add_pre_processed_content(self, site, pre_processed_content, cpath=None):
            self.__pre_processed_cachemap[site.id][pre_processed_content.curl] = pre_processed_content
            if cpath is not None:
                self.__cpath_to_pre_processed_contents[site.id][cpath] = pre_processed_content

        def get_pre_processed_content_by_curl(self, site, curl, default=None):
            return self.__pre_processed_cachemap[site.id].get(curl, default)

        def get_pre_processed_content_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_pre_processed_contents[site.id].get(cpath, default)

        def add_marked_content(self, site, marked_content):
            # TODO: set limit to 100 or so
            self.__marked_contents_cachemap[site.id][marked_content.curl] = marked_content
            self.__cpath_to_marked_content[site.id][marked_content.cpath] = marked_content

        def get_marked_content_by_curl(self, site, curl, default=None):
            return self.__marked_contents_cachemap[site.id].get(curl, default)

        def get_marked_content_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_marked_content[site.id].get(cpath, default)

        def add_marked_cfields(self, site, cfields):
            self.__marked_cfields_cachemap[site.id][cfields.curl] = cfields
            self.__cpath_to_marked_cfields[site.id][cfields.cpath] = cfields

        def get_marked_cfields_by_curl(self, site, curl, default=None):
            return self.__marked_cfields_cachemap[site.id].get(curl, default)

        def get_marked_cfields_by_cpath(self, site, cpath, default=None):
            return self.__cpath_to_marked_cfields[site.id].get(cpath, default)

        def get_marked_cpath_by_curl(self, site, curl, default=None):
            cfs = self.get_marked_cfields_by_curl(site, curl, None)
            if cfs is None:
                return default
            else:
                return cfs.cpath

        def get_all_marked_cfields(self, site):
            return tuple(self.__marked_cfields_cachemap[site.id].values())

        def add_marker(self, site, marker_id, marker):
            self.__marker_by_id_cachemap[site.id][marker_id] = marker

        def get_marker(self, site, marker_id, default=None):
            return self.__marker_by_id_cachemap[site.id].get(marker_id, default)

        def get_markers(self, site):
            return tuple(self.__marker_by_id_cachemap[site.id].values())

        def add_syd(self, site, cpath, syd):
            self.__cpath_to_syd_cachemap[site.id][cpath] = syd

        def get_syd(self, site, cpath, default=None):
            return self.__cpath_to_syd_cachemap[site.id].get(cpath, default)

        def add_menu(self, site, menu_name, menu):
            self.__menus_cachemap[site.id][menu_name] = menu

        def get_menu(self, site, menu_name, default=None):
            menu = self.__menus_cachemap[site.id].get(menu_name, None)
            if menu is None:
                return default
            return menu

        def get_menus(self, site):
            return tuple(self.__menus_cachemap[site.id].values())

        def add_model(self, site, model):
            self.__models_cachemap[site.id][model.model_name] = model
            return model

        def get_model(self, site, model_name, default=None):
            return self.__models_cachemap[site.id].get(model_name, default)

        def add_user(self, site, user):
            self.__users_cachemap[site.id][user.id] = user

        def get_user(self, site, user_id, default=None):
            return self.__users_cachemap[site.id].get(user_id, default)

        def clear_content_cache(self, site):
            self.__pre_processed_cachemap[site.id].clear()
            self.__marked_contents_cachemap[site.id].clear()
            self.__marked_cfields_cachemap[site.id].clear()
            self.__cpath_to_pre_processed_contents[site.id].clear()
            self.__cpath_to_marked_content[site.id].clear()
            self.__cpath_to_marked_cfields[site.id].clear()

        def clear_marker_cache(self, site):
            self.__marker_by_id_cachemap[site.id].clear()

        def clear_syd_cache(self, site):
            self.__cpath_to_syd_cachemap[site.id].clear()

        def clear_menus_cache(self, site):
            self.__menus_cachemap[site.id].clear()

        def clear_model(self, site):
            self.__models_cachemap[site.id].clear()

        def clear_users(self, site):
            self.__users_cachemap[site.id].clear()

        def clear_cache(self, site):
            """Clear all"""
            self.clear_content_cache(site)
            self.clear_marker_cache(site)
            self.clear_syd_cache(site)
            self.clear_menus_cache(site)
            self.clear_model(site)
            self.clear_users(site)
