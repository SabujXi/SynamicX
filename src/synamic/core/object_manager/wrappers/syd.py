from synamic.core.parsing_systems.curlybrace_parser import SydParser


class SydObject:
    def __init__(self, syd, object_id):
        assert isinstance(syd, SydParser), 'Invalid object provided'
        self._syd = syd
        self._object_id = object_id
