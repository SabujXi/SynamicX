"""
Synamic Data Classes
"""
import re
import enum
import collections
import datetime
import numbers


class _Patterns:
    interpolation_identifier = re.compile(r'(?<!\$)\$\{[ \t]*(?P<identifier>'
                                          r'[a-z_][a-z0-9_]*)[ \t]*\}', re.I)  # escape $ with another - that simple


@enum.unique
class SydDataType(enum.Enum):
    number = 1
    date = 2
    time = 3
    datetime = 4
    string = 5

    # data structures
    # block = 6 # map
    # block_list = 7
    # inline_list = 8


syd_to_py_types = {
    SydDataType.time: (datetime.time,),
    SydDataType.date: (datetime.date,),
    SydDataType.datetime: (datetime.datetime,),
    SydDataType.number: (numbers.Number, int, float),
    SydDataType.string: (str,)
}

py_to_syd_types = {}
for syd_type, py_types in syd_to_py_types.items():
    for py_type in py_types:
        py_to_syd_types[py_type] = syd_type


class _SydData:
    @property
    def key(self):
        raise NotImplemented

    @property
    def is_scalar(self):
        return type(self) is SydData

    @property
    def is_container(self):
        return type(self) is SydContainer

    def syd_set_parent(self, p):
        raise NotImplemented

    def set_converter(self, c):
        raise NotImplemented

    def set_converted(self, v):
        raise NotImplemented

    @property
    def converter(self):
        raise NotImplemented


class SydData(_SydData):  # Previously SydScalar.
    def __init__(self, key, value, datatype=None, parent_container=None, converter=None, converted_value=None):
        if key is not None:
            assert '.' not in key, f'Key {key} is invalid where value is {value}'
        # assert isinstance(value, syd_to_py_types[datatype])
        # scalar can be of any type - any valid python object except isinstance(o, [list, tuple, dict]).
        # It doesn't always have to be type form syd string or file.
        assert value is not None, 'None is not allowed'
        assert not isinstance(value, (list, tuple, dict)), \
            'Scalar value cannot be of instance of list, tuple or dict. Use SydContainer for them.'
        self.__key = key
        self.__value = value
        self.__datatype = datatype
        self.__converter = converter
        self.__converted_value = converted_value
        self.__parent_container = None

        self.__cached_interpolated_str = None
        self.syd_set_parent(parent_container)

    def clone(self, parent_container=None, converter=None, converted_value=None):
        if converter is None:
            converter = self.__converter
        if converted_value is None:
            converted_value = self.__converted_value
        return self.__class__(self.__key, self.__value, self.__datatype, parent_container=parent_container, converter=converter, converted_value=converted_value)

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        if self.__converted_value is not None:
            value = self.__converted_value
        else:
            if not callable(self.__converter):
                value = self.__value
            else:
                value = self.__converter(self.__value)
                assert value is not None
                self.__value = value
        return value

    @property
    def value_origin(self):
        return self.__value

    def set_converted(self, value):
        assert value is not None
        self.__converted_value = value

    @property
    def type(self):
        return self.__datatype

    def syd_set_parent(self, p):
        assert type(p) in (SydContainer, type(None))
        assert self.__parent_container is None, 'Cannot re-set parent'
        self.__parent_container = p

        # process interpolation
        if p is not None:
            value = self.__value
            # process interpolation for string
            if self.__datatype is SydDataType.string:
                if self.__cached_interpolated_str is not None:
                    value = self.__cached_interpolated_str
                else:
                    value = self.__cached_interpolated_str = _Patterns.interpolation_identifier.sub(self.__interpolation_replacer,
                                                                                                    value)
            self.__value = value

    def set_converter(self, converter):
        assert not callable(self.__converter)
        self.__converter = converter

    @property
    def converter(self):
        return self.__converter

    def __str__(self):
        if self.key is not None:
            return "%s => %s" % (self.key, str(self.value))
        else:
            return str(self.value)

    def __repr__(self):
        return repr(self.__str__())

    def __interpolation_replacer(self, match):
        identifier = match.group('identifier')
        assert self.__key != identifier, 'Key is being interpolated recursively: %s' % identifier
        if self.__parent_container is not None:
            v = self.__parent_container.get(identifier, '')
            assert type(v) in (int, float, str), 'Only number and string data can be interpolated in' \
                                                 'to a string. Data with' \
                                                 ' kye `%s` is of type `%s`' % (self.key, str(type(v)))
            v = str(v)  # convert it in case it is a number.
            return v
        else:
            raise Exception('Parent for key `%s` is set to None' % str(self.__key))


class SydContainer(_SydData):
    def __init__(self, key=None, initial_data=(), is_list=False, parent_container=None, converter=None, converted_value=None, read_only=False):
        if key is not None:
            assert '.' not in key
        self.__key = key
        self.__is_list = is_list
        self.__data_list = []
        self.__data_list_index_map = {}
        self.__parent_container = None  # parent_container from init will be set through a method below.
        self.__converter = converter
        self.__converted_value = converted_value
        self.__read_only = read_only

        self.syd_set_parent(parent_container)

        for data in initial_data:
            self.add(data)

    @property
    def parent(self):
        return self.__parent_container

    def clone(self, parent_container=None, converter=None, converted_value=None, read_only=False):
        if converter is None:
            converter = self.__converter
        if converted_value is None:
            converted_value = self.__converted_value
        cln = self.__class__(
            self.__key,
            is_list=self.__is_list,
            parent_container=parent_container,
            converter=converter,
            converted_value=converted_value,
            read_only=read_only
        )
        for data in self.__data_list:
            cln.add(data.clone())
        return cln
    copy = clone

    def new(self, *others):
        assert not self.is_list, 'Cannot create new from list, it must be a block'
        self_clone = self.clone()
        for other in others:
            assert not other.is_list, 'Cannot create new with list, need block'
            for idx, o_c in enumerate(other.clone_children()):
                if self_clone.is_list:
                    key = idx
                    self_clone.add(o_c)
                else:
                    key = o_c.key
                    if key in self_clone:
                        self_clone.update(key, o_c)
                    else:
                        self_clone.add(o_c)
        return self_clone

    def merged_new(self, *other_containers):
        new_container = self.clone()
        for other_container in other_containers:
            assert isinstance(other_container, SydContainer)
            for key in other_container.keys():
                other_data = other_container.get_child(key)
                old_data = new_container.get_child(key, error_out=False)

                if old_data is None:
                    new_container.add(other_data.clone())
                else:
                    if isinstance(old_data, SydData):
                        assert isinstance(other_data, SydData)
                        new_container.update(key, other_data.clone())
                    else:
                        assert isinstance(other_data, SydContainer) and isinstance(old_data, SydContainer)
                        merged_children = old_data.merged_new(other_data)
                        new_container.add(merged_children)
        return new_container

    @property
    def is_root(self):
        return self.__parent_container is None or self.__key in ('__root__', None)

    def get_children(self):
        return tuple(self.__data_list)

    def clone_children(self):
        return tuple(e.clone() for e in self.get_children())

    def get_child(self, key, multi=False, error_out=True):
        assert isinstance(key, (int, str, list, tuple)), \
            f'Only integer and string keys are accepted, you provided key of type: {type(key)}'
        key = int(key) if type(key) is str and key.isdigit() else key

        if type(key) is int:
            assert self.is_list, \
                f"Index {key} provided for a block collection. Use numeric index only for list collections"
            try:
                d = self.__data_list[key]
                if multi:
                    d = (d, )
            except IndexError:
                if not error_out:
                    return None
                else:
                    raise IndexError(f'{key} does not exist')
        else:
            if isinstance(key, (list, tuple)):
                keys = key
            else:
                keys = key.split('.')
            try:
                first_key = keys[0]
                syds = []
                for idx in self.__data_list_index_map[first_key]:
                    syds.append(self.__data_list[idx])

                keys = keys[1:]
                last_idx = len(keys) - 1
                for idx, _key in enumerate(keys):
                    if last_idx == idx:
                        if not syds[-1].is_container:
                            # print('Found value is not a block - it is a scalar')
                            raise KeyError('Found value is not a block - it is a scalar')
                    _ = syds[-1].get_child(_key, multi=multi)

                    if multi:
                        syds = _
                    else:
                        syds = [_, ]

                if multi:
                    d = syds
                else:
                    d = syds[-1]
            except KeyError:
                if not error_out:
                    return None
                else:
                    raise KeyError(f'Key `{key}` was not found')
        return d

    def get(self, key, default=None, multi=False):
        try:
            value = self.get_child(key, multi=multi)
            if not multi:
                value = value.value
            else:
                _values = value
                _ = []
                for v in _values:
                    _.append(v.value)
                value = tuple(_)
        except (KeyError, IndexError):
            value = default
        return value

    def __getitem__(self, key):
        value = self.get(key, default=None, multi=False)
        if value is None:
            raise KeyError(f'Key `{key}` was not found')
        return value

    @property
    def is_list(self):
        return self.__is_list

    @property
    def key(self):
        return self.__key

    def keys(self):
        """Own keys"""
        l = list()
        if self.is_list:
            l = list(range(len(self.__data_list)))
        else:
            for e in self.__data_list:
                if e.key is not None:
                    l.append(e.key)
        return tuple(l)

    def values(self):
        """Values are not converted!!!"""
        l = list()
        for e in self.__data_list:
            value = e.value
            l.append(value)
        return tuple(l)

    def items(self):
        """Values are not converted!!!"""
        l = []
        for i, e in enumerate(self.__data_list):
            value = e.value
            if self.is_list:
                l.append((i, value))
            else:
                l.append((e.key, value))
        return tuple(l)

    def add(self, *args):
        assert not self.__read_only
        # args validating, parsing, and constructing value called syd.
        assert len(args) in (1, 2), f'Not enough or more than enough args: {args}'
        parent_container = self
        if len(args) == 2:
            assert not self.is_list, \
                '2 args provided for a list, where the first arg is considered key and the second as data/value'
            key = args[0]
            value = args[1]
            # key must be string
            assert isinstance(key, str),\
                'The first arg must be of type string as that is the key when second arg exists'
            # value must not be syd data or container.
            assert not isinstance(value, _SydData), \
                'The second arg cannot be of type Scalar or Container - they do not need key, they already have one'
            if isinstance(value, (list, tuple, dict)):
                syd = self.__create_container_from_vector(key, value)
            else:
                syd = SydData(key, value)

            # calculating the parent
            key = syd.key
            keys = key.split('.')
            if len(keys) > 1:
                comps = key.split('.')[:-1]
                parent_container = self.get_child(comps, multi=False)
                assert parent_container.is_container

        else:  # len == 1
            value = args[0]
            assert isinstance(value, _SydData),\
                'When only one arg is passed there is no key info and thus it must be _SydData instance'
            syd = value

        # adding the value to the container.
        assert isinstance(syd, _SydData)
        self.__data_list.append(syd)
        if not self.is_list:
            idx = len(self.__data_list) - 1
            key = syd.key
            if key not in self.__data_list_index_map:
                data_l = []
                self.__data_list_index_map[key] = data_l
            else:
                data_l = self.__data_list_index_map[key]
            # data_l.append((idx, syd)), now only one source of truth against two before - previously: data list, map
            data_l.append(idx)
        syd.syd_set_parent(parent_container)

    @staticmethod
    def __create_container_from_vector(key, vector):
        assert isinstance(vector, (list, tuple, dict))
        is_map = isinstance(vector, dict)
        if is_map:
            syd = SydContainer(key, is_list=False)
            for k, v in vector.items():
                syd.add(k, v)
        else:
            syd = SydContainer(key, is_list=True)
            for v in vector:
                syd.add(v)
        return syd

    def set(self, key, py_value):
        """
        Sets py value as converted to existing key
        BUT for non existing value it uses add()
        """
        assert not self.__read_only
        assert not isinstance(py_value, _SydData)
        try:
            syds = self.get_child(key, multi=True)
            for syd in syds:
                syd.set_converted(py_value)
        except KeyError:
            self.add(key, py_value)

    def update(self, key_idx, syd_data):
        assert isinstance(syd_data, _SydData)
        assert key_idx is not None
        if isinstance(key_idx, int):
            assert syd_data.key is None
            self.__data_list[key_idx] = syd_data
            return

        if isinstance(key_idx, (list, tuple)):
            keys = key_idx
        else:
            keys = key_idx.split('.')

        if len(keys) == 1:
            key_idx = keys[0]
            indices = self.__data_list_index_map[key_idx]
            idx = indices[-1]
            self.__data_list[idx] = syd_data
            syd_data.syd_set_parent(self)
        else:
            parent_keys = keys[:-1]
            key_idx = keys[-1]
            parent_syd = self.get_child(parent_keys)
            parent_syd.update(key_idx, syd_data)

    def __setitem__(self, key, value):
        assert not self.__read_only
        self.set(key, value)

    def lock(self):
        assert not self.__read_only
        self.__read_only = True
        for d in self.__data_list:
            if isinstance(d, self.__class__):
                d.lock()

    # deleting
    def __remove_from_self(self, key):
        key = int(key) if type(key) is str and key.isdigit() else key
        if self.is_list:
            # list indexes are not cached in the map
            del self.__data_list[key]
        else:
            indices = self.__data_list_index_map[key]
            indices.reverse()  # start deleting from larger index
            # delete from map
            del self.__data_list_index_map[key]
            # delete from ordered list
            for idx in indices:
                del self.__data_list[idx]

            # map
            new_map = type(self.__data_list_index_map)()
            for idx, elem in enumerate(self.__data_list):
                if elem.key not in new_map:
                    l = []
                    new_map[elem.key] = l  # Here was that deadly bug
                else:
                    l = new_map[elem.key]
                l.append(idx)
            self.__data_list_index_map = new_map

    def __delitem__(self, key):
        assert not self.__read_only
        assert type(key) in (int, str), \
            f'Only integer and string keys are accepted, you provide key of type: {type(key)}'
        key = str(key)  # TODO: handle int key specially for performance.
        keys = key.split('.')
        key2del = keys[-1]
        keys = keys[:-1]

        try:
            if len(keys) == 0:
                cont = self
            else:
                k = keys[0]
                keys = keys[1:]
                cont = self.get_child(k)
                for k in keys:
                    cont = cont._get_original(k)
            cont.__remove_from_self(key2del)
        except (KeyError, IndexError):
            # raise
            raise KeyError(f'Key/index `{key}` was not found. Keys: {self.keys()}')

    def __contains__(self, key_value):
        if self.is_list:
            value = key_value
            res = False
            for data in self.__data_list:
                if data.value == value:
                    res = True
                    break
            return res
        else:
            key = key_value
            res = self.get(key, None)
            return False if res is None else True

    def key_exists(self, key):
        return key in self

    @property
    def value(self):
        if self.__converted_value is not None:
            value = self.__converted_value
        else:
            if callable(self.__converter):
                value = self.__converter(self.value_origin)
                assert value is not None
                self.__converted_value = value
            else:
                # value = self.value_origin
                value = self
                # if self.is_list:
                #     value = self.as_tuple
                # else:
                #     value = self.as_dict
        return value

    @property
    def value_origin(self):
        if self.is_list:
            return self.as_tuple
        else:
            return self.as_dict

    def syd_set_parent(self, p):
        assert type(p) in (type(None), self.__class__), 'Invalid type: %s' % str(type(p))
        assert self.__parent_container is None, 'Cannot re-set parent container'
        self.__parent_container = p

    # conversion
    @property
    def converter(self):
        return self.__converter

    def set_converter(self, converter):
        assert not callable(self.__converter)
        assert not self.is_root
        self.__converter = converter

    def set_converted(self, value):
        assert value is not None
        assert not self.is_root
        self.__converted_value = value

    def set_converter_for(self, key, converter):
        syds = self.get_child(key, multi=True)
        for syd in syds:
            syd.set_converter(converter)

    # iter
    def __iter__(self):
        if self.is_list:
            return iter(self.values())
        else:
            return iter(self.keys())

    # as vector
    @property
    def as_tuple(self):
        assert self.is_list
        c = []
        for d in self.__data_list:
            c.append(d.value)
        c = tuple(c)
        return c

    @property
    def as_dict(self):
        assert not self.is_list
        c = collections.OrderedDict()
        for d in self.__data_list:
            c[d.key] = d.value
        return c

    # as string
    def __str__(self):
        l = []
        for e in self.__data_list:
            l.append(str(e))
        if self.is_list:
            data_text = ", ".join(l)
        else:
            data_text = "\n".join(l)
        if self.key is not None:
            return str(self.key) + " { %s }" % data_text
        else:
            res = "{ %s }" % data_text
            return res

    def __repr__(self):
        return repr(self.__str__())