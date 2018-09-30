from synamic.core.object_manager.object_id import ObjectId


class ObjectManager:
    def get(self, object_id, default=None):
        self.__check_object_id_type(object_id)
        if object_id.type == 'SYD_FILE':
            # if database mode/dev mode/prod mode.
            pass

        return self.__object_map.get(object_id, default)

    def __init__(self, synamic):
        self.__synamic = synamic

        self.__object_map = {}

    @staticmethod
    def __check_object_id_type(object_id):
        assert type(object_id) is ObjectId, 'id of object must be of type ObjectId, %s provided' % str(object_id)

    def __add(self, _object, object_id, depends_ids=()):
        self.__check_object_id_type(object_id)

        self.__object_map[_object.id] = _object

    def remove(self, object_id):
        self.__check_object_id_type(object_id)
        del self.__object_map[object_id]

    def clear(self):
        self.__object_map.clear()

    def length(self):
        return len(self.__object_map)
