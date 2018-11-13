class Hashable:
    """A container to make hashable of any object so that
    we can use that object anywhere hashing is needed.
    e.g. set or dict operations"""
    __instance_count = 0

    def __init__(self, obj):
        __id = self.__instance_count = self.__instance_count + 1
        self.__id = __id
        self.__obj = obj

    @property
    def id(self):
        return self.__id

    @property
    def origin(self):
        return self.__obj

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__id == other.id

    def __hash__(self):
        return hash(self.__id)

    def __str__(self):
        return str(self.__obj)

    def __repr__(self):
        return repr(self.__obj)
