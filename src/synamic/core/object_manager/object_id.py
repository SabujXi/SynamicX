import re


class _Patterns:
    data_id = re.compile(r'^[^\s\n\t:]?[^\n\t:]+[^\s\n\t:]?$')  # TODO: make it NTFS (or more) file name compliant.


class ObjectId:
    def __init__(self, object_id, object_type):
        assert type(object_id) is str, 'object_id must be of type string, %s type found' % str(type(object_id))
        assert type(object_type) is str, 'object_type must be represented as string, %s type found' % str(type(object_type))
        assert _Patterns.data_id.match(object_id), 'Object id did not match the pattern: %s. Check the pattern and ' \
                                                 'check whether id starts or ends with space chars' % object_id
        self.__object_id = object_id
        self.__object_type = object_type

    @property
    def id(self):
        return self.__object_id

    @property
    def type(self):
        return self.__object_type

    def __hash__(self):
        return hash(self.__object_id)

    def __eq__(self, other):
        return self.__object_type == other.type and self.__object_id == other.id

