import re
from synamic.core.contracts import CDocType
from synamic.exceptions import SynamicMarkerIsNotPublic

_mark_title2id_sub_pat = re.compile(r'[\s:-]')

separator_comma_pat = re.compile(r',[^,]?')


class _Mark:
    def __init__(self, parent, site, mark_map, marker):
        if mark_map.get('title', None) is None:
            root, path = self._root_path
            raise Exception('title was not found in path %s of marker %s'
                            '' % (str(root.id), ':'.join(path)))
        self.__parent = parent
        self.__site = site
        self.__mark_map = mark_map
        self.__marker = marker

        # content(s)
        self.__content = None
        self.__synthetic_cfields = None

    @property
    def _parent(self):
        return self.__parent

    @property
    def _root_path(self):
        paths = []
        parent = self._parent
        while True:
            parent = parent._parent
            if type(parent) is not Marker:
                paths.append(parent.title)
            else:
                break
        root = parent
        paths.reverse()
        return root, tuple(paths)

    @staticmethod
    def title_to_id(title):
        title = title.strip()
        title = title.lower()
        # replace consecutive space chars with single one
        title = ' '.join(title.split())
        # replace no alpha-numeric-dash-underscore chars with a single underscore.
        _id = _mark_title2id_sub_pat.sub('_', title)
        return _id

    @property
    def marker(self):
        return self.__marker

    @property
    def title(self):
        return self.__mark_map['title']

    @property
    def id(self):
        # TODO: create id from title in a better way
        _id = self.__mark_map.get('id', None)
        if _id is None:
            _id = self.title_to_id(self.title)
        return _id

    @property
    def description(self):
        return self.__mark_map.get('description', '')

    @property
    def marks(self):
        return self.__mark_map.get('marks', None)

    @property
    def cfields(self):
        if not self.__marker.is_public:
            raise SynamicMarkerIsNotPublic(
                f'Marker with title {self.__marker.title} is not public and thus the mark title {self.title} cannot '
                f'have cfields'
            )
        if self.__synthetic_cfields is not None:
            sf = self.__synthetic_cfields
        else:
            system_settings = self.__site.system_settings
            content_service = self.__site.get_service('contents')
            url_partition_comp = system_settings['url_partition_comp']
            mark_url_comp = system_settings['mark_url_comp']
            cdoctype = CDocType.GENERATED_HTML_DOCUMENT
            marker_slug = self.__marker.get('slug', None)
            if marker_slug is None:
                marker_slug = self.__marker.id
            curl = self.__site.synamic.router.make_url(
                self.__site, f'/{url_partition_comp}/{mark_url_comp}/{marker_slug}/{self.id}', for_cdoctype=cdoctype
            )
            mimetype = 'text/html'
            sf = synthetic_fields = content_service.make_synthetic_cfields(
                curl,
                cdoctype,
                mimetype,
                cpath=None,
                fields_map=None)
            sf['title'] = self.title
            sf['mark'] = self
            sf['marker'] = self.__marker
            self.__synthetic_cfields = synthetic_fields
            # TODO: create single marker.html template for all and then specific marker id based template?
            # Add such settings to site settings.
        return sf

    @property
    def curl(self):
        return self.cfields.curl

    def __marker_content_renderer(self, site, gen_content):
        site_settings = site.settings
        template_service = site.get_service('templates')
        user_template_name = site_settings['templates.mark']

        html_text_content = template_service.render(
            user_template_name,
            site=site,
            content=gen_content,
            mark=self,
            marker=self.__marker
        )
        return html_text_content

    @property
    def content(self):
        if not self.__marker.is_public:
            raise SynamicMarkerIsNotPublic(
                f'Marker with title {self.__marker.title} is not public and thus the mark title {self.title} cannot '
                f'have content'
            )
        if self.__content is not None:
            content = self.__content
        else:
            content_service = self.__site.get_service('contents')
            content = content_service.build_generated_content(
                self.cfields,
                '',
                source_cpath=None,
                render_callable=self.__marker_content_renderer)
            self.__content = content
        return content

    @property
    def contents(self):
        if not self.__marker.is_public:
            raise SynamicMarkerIsNotPublic(
                f'Marker with title {self.__marker.title} is not public and thus the mark title {self.title} cannot '
                f'have contents'
            )

        if self.__marker.type == 'single':
            query = f'{self.marker.id} == {self.title} :sortby created_on desc'
        else:
            query = f'{self.marker.id} contains {self.title} :sortby created_on desc'
        contents = self.__site.object_manager.query_contents(query)
        return tuple(contents)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id and self.marker == other.marker

    def __hash__(self):
        return hash(self.id + self.marker.id)

    def __getattr__(self, key):
        return self.__mark_map.get(key, '')

    def __str__(self):
        return "Mark: %s" % self.title

    def __repr__(self):
        return repr(self.__str__())


class Marker:
    def __init__(self, site, marker_id, marker_type, marker_title, marker_mark_maps, origin_syd):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        self.__site = site
        self.__id = marker_id
        self.__title = marker_title
        self.__type = marker_type
        # self.__marks_list = mark_maps

        self.__marks_by_title = {}
        self.__marks_by_id = {}

        self.__marks = []
        __marks = []
        self.__process_marks_list(marker_mark_maps, __marks, parent=None)
        self.__origin_syd = origin_syd
        for mark in __marks:
            self.add_mark(mark)

    def make_mark(self, mark_map, parent=None):
        return _Mark(parent, self.__site, mark_map, self)

    def make_mark_by_title(self, title_str, parent=None):
        # TODO: should be empty syd?
        mark_map = {}
        title_str = title_str.strip()
        mark_map['title'] = title_str
        return self.make_mark(mark_map, parent=parent)

    def add_mark(self, mark):
        assert type(mark) is _Mark
        assert mark.id not in self.__marks_by_id, f'{mark.id}'
        self.__marks.append(mark)
        self.__marks_by_title[_Mark.title_to_id(mark.title)] = mark
        self.__marks_by_id[mark.id] = mark

    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title

    @property
    def type(self):
        return self.__type

    @property
    def is_public(self):
        public = self.get('is_public', None)
        if public is None or public:
            return True
        return False

    @property
    def is_single(self):
        return self.type == 'single'

    @property
    def is_multiple(self):
        return self.type == 'multiple'

    @property
    def is_hierarchical(self):
        return self.type == 'hierarchical'

    @property
    def marks(self):
        return tuple(self.__marks)

    def get_mark_by_id(self, id, default=None):
        return self.__marks_by_id.get(id, default)

    def get_mark_by_title(self, title, default=None):
        return self.__marks_by_title.get(_Mark.title_to_id(title), default)

    def __process_marks_list(self, mark_maps, res_mark_objs, parent):
        _marks = []
        for mark_map in mark_maps:
            _marks.append(self.make_mark(mark_map, parent))

        if res_mark_objs is not None:
            res_mark_objs.extend(_marks)

        if self.is_hierarchical:
            for _mark in _marks:
                _mark_maps = _mark.marks
                if _mark_maps is not None:
                    self.__process_marks_list(_mark_maps, res_mark_objs, _mark)

    def get(self, key, default=None):
        return self.__origin_syd.get(key, default=default)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.__id)
