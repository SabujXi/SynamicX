import re

_mark_title2id_sub_pat = re.compile(r'[^a-zA-Z0-9_-]')


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

    @property
    def marker(self):
        return self.__marker

    @property
    def title(self):
        return self.__mark_map['title']

    @property
    def id(self):
        # TODO: create id from title
        _id = self.__mark_map.get('id', None)
        if _id is None:
            _id = _mark_title2id_sub_pat.sub(self.title, '_')
        return _id

    @property
    def description(self):
        return self.__mark_map.get('description', '')

    @property
    def marks(self):
        return self.__mark_map.get('marks', None)

    def __getattr__(self, key):
        return self.__mark_map.get(key, '')


class Marker:
    def __init__(self, site, marker_id, marker_type, marker_title, marker_mark_maps):
        assert marker_type in {'single', 'multiple', 'hierarchical'}
        self.__site = site
        self.__id = marker_id
        self.__title = marker_title
        self.__type = marker_type
        # self.__marks_list = mark_maps

        self.__marks_by_title = {}
        self.__marks_by_id = {}

        self.__marks = []
        self.__process_marks_list(marker_mark_maps, self.__marks, parent=self)

        for mark in self.__marks:
            self.__marks_by_title[mark.title] = mark
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
        return self.__marks_by_title.get(title, default)

    def __process_marks_list(self, mark_maps, res_mark_objs, parent):
        _marks = []
        for mark_map in mark_maps:
            _marks.append(_Mark(parent, self.__site, mark_map, self))

        if res_mark_objs is not None:
            res_mark_objs.extend(_marks)

        if self.is_hierarchical:
            for _mark in _marks:
                _mark_maps = _mark.get('marks', None)
                if _mark_maps is not None:
                    self.__process_marks_list(_mark_maps, res_mark_objs, _mark)
