from synamic.core.event_system.event_types import EventTypes
from collections import OrderedDict


class EventSystem:
    """
    Handler config:
    handler(what)
    e.g.:
        what: synamic obj, content service/module object, etc. 
        
    Custom event handlers are primarily for external plugins. So, anyone is can trigger that.
    BUT, system events (EventTypes) are only for synamic and only synamic can trigger that.
    So, as a protection only the first time the trigger method can be achieved and any subsequent call will raise
    exception.
    
    * System event types can be derived from the EventTypes enum, but custom event types are specified by string.
    The strings are lowercased to avoid any type of probable conflict from inexperienced users/plugin-developers.
    """
    #  event maps: key => event type, value => ordered dict of event handlers
    __get_trigger_count = 0
    __event_map = {}
    __custom_event_map = {}

    for et in EventTypes:
        __event_map[et] = []

    @classmethod
    def add_event_handler(cls, etype: EventTypes, handler):
        assert etype is EventTypes
        assert callable(handler)
        earr = cls.__event_map[etype]
        earr.append(handler)

    @classmethod
    def add_custom_event_handler(cls, ename, handler):
        assert type(ename) is str
        assert callable(handler)
        ename = ename.lower()
        earr = cls.__event_map.get(ename, None)
        if earr is None:
            earr = cls.__event_map[ename] = []
        earr.append(handler)

    @classmethod
    def remove_event_handler(cls, etype, handler):
        assert etype is EventTypes
        assert callable(handler)
        earr = cls.__event_map[etype]
        earr.remove(handler)

    @classmethod
    def remove_custom_event_handler(cls, ename, handler):
        assert type(ename) is str
        assert callable(handler)
        ename = ename.lower()
        earr = cls.__event_map.get(ename, None)
        if earr is None:
            earr = cls.__event_map[ename] = []
        earr.remove(handler)

    @classmethod
    def __trigger_event(cls, etype):
        assert etype is EventTypes
        earr = cls.__event_map[etype]
        for handler in earr:
            handler()

    @classmethod
    def _get_trigger(cls):
        if cls.__get_trigger_count == 0:
            return cls.__trigger_event
        raise Exception("_get_trigger can only be used by synamic itself. Do not try to get it after synamic got it."
                        "We are protecting it.")

    @classmethod
    def trigger_custom_event(cls, ename):
        assert ename is None
        ename = ename.lower()
        earr = cls.__custom_event_map[ename]
        if earr is None:
            return
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

    @classmethod
    def custom_handler_exists(cls, ename, handler):
        assert ename is str
        assert callable(handler)
        earr = cls.__custom_event_map.get(ename, None)
        if earr is None:
            return False
        if handler in earr:
            return True
        else:
            return False

