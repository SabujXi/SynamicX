from synamic.core.event_system.event_types import EventTypes
from collections import OrderedDict


class EventSystem:
    """
    Handler config:
    handler(what)
    e.g.:
        what: synamic obj, content service/module object, etc. 
    """
    #  event maps: key => event type, value => ordered dict of event handlers
    __event_map = {}

    for et in EventTypes:
        __event_map[et] = []

    @classmethod
    def add_event_handler(cls, etype: EventTypes, handler):
        assert etype is EventTypes
        assert callable(handler)
        earr = cls.__event_map[etype]
        earr.append(handler)

    @classmethod
    def remove_event_handler(cls, etype, handler):
        assert etype is EventTypes
        assert callable(handler)
        earr = cls.__event_map[etype]
        earr.remove(handler)

    @classmethod
    def trigger_event(cls, etype):
        assert etype is EventTypes
        earr = cls.__event_map[etype]
        for handler in earr:
            handler()

    @classmethod
    def handler_exists(cls, etype, handler):
        assert etype is EventTypes
        assert callable(handler)
        earr = cls.__event_map[etype]
        if handler in earr:
            return True
        else:
            return False
