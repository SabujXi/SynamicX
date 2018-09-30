from synamic.core.parsing_systems.curlybrace_parser import Syd


class SydObject:
    def __init__(self, syd, object_id):
        assert isinstance(syd, Syd), 'Invalid object provided'
        self._syd = syd
        self._object_id = object_id
