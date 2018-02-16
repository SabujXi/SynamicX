from synamic.core.event_system.event_types import EventTypes
from synamic.core.exceptions.synamic_exceptions import LogicalError


def _not_completed_decorator(method):
    def method_wrapper(self, *args, **kwargs):
        if self.completed:
            raise LogicalError("This method (%s) can only be used when the event was not completed" % method.__name__)
        return method(self, *args, **kwargs)
    return method_wrapper


class Event:
    def __init__(self, subject, **kwargs):
        self.__subject = subject
        self.__completed = False
        self.__container = {}
        self.__container.update(kwargs)

    @property
    @_not_completed_decorator
    def subject(self):
        return self.__subject

    @property
    def completed(self):
        return self.__completed

    @_not_completed_decorator
    def mark_complete(self):
        self.__completed = True
        del self.__subject
        self.__container.clear()
        del self.__container

    @_not_completed_decorator
    def get(self, key, *args, **kwargs):
        return self.__container.get(key, *args, **kwargs)

    @_not_completed_decorator
    def keys(self):
        return self.__container.keys()

    @_not_completed_decorator
    def values(self):
        return self.__container.values()

    @_not_completed_decorator
    def items(self):
        return self.items()

    @_not_completed_decorator
    def __getitem__(self, item):
        return self.__container.__getitem__(item)

    @_not_completed_decorator
    def __setitem__(self, key, value):
        return self.__container.__setattr__(key, value)

    @_not_completed_decorator
    def __iter__(self):
        return self.__container.__iter__()

    @_not_completed_decorator
    def __contains__(self, item):
        return self.__container.__contains__(item)


class Handler:
    def __init__(self, handler_callable):
        assert callable(handler_callable)
        self.__handler_callable = handler_callable

    def __call__(self, event, **kwargs):
        assert type(event) is Event
        return self.__handler_callable(event, **kwargs)


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
    
    Handler functions will be called with an event object. An event object will hold a subject,
    and a map of other objects where strings are used as keys.
    
    """
    #  event maps: key => event type, value => ordered dict of event handlers
    __get_trigger_count = 0
    __event_map = {}
    __custom_event_map = {}

    # will use the following when an int will be used to cancel a registered event
    __last_event_id = 0
    __last_custom_event_id = 0

    for et in EventTypes:
        __event_map[et] = []

    @classmethod
    def add_event_handler(cls, etype: EventTypes, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = cls.__event_map[etype]
        earr.append(handler)

    @classmethod
    def add_custom_event_handler(cls, ename, handler):
        assert type(ename) is str
        assert type(handler) is Handler
        ename = ename.lower()
        earr = cls.__event_map.get(ename, None)
        if earr is None:
            earr = cls.__event_map[ename] = []
        earr.append(handler)

    @classmethod
    def remove_event_handler(cls, etype, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = cls.__event_map[etype]
        earr.remove(handler)

    @classmethod
    def remove_custom_event_handler(cls, ename, handler):
        assert type(ename) is str
        assert type(handler) is Handler
        ename = ename.lower()
        earr = cls.__event_map.get(ename, None)
        if earr is None:
            earr = cls.__event_map[ename] = []
        earr.remove(handler)

    @classmethod
    def __trigger_event(cls, etype, event):
        assert type(etype) is EventTypes
        assert type(event) is Event
        earr = cls.__event_map[etype]
        for handler in earr:
            handler(event)

    @classmethod
    def _get_trigger(cls):
        if cls.__get_trigger_count == 0:
            return cls.__trigger_event
        raise LogicalError("_get_trigger can only be used by synamic itself. Do not try to get it after synamic got it."
                        "We are protecting it.")

    @classmethod
    def trigger_custom_event(cls, ename, event):
        assert ename is None
        assert type(event) is Event
        ename = ename.lower()
        earr = cls.__custom_event_map[ename]
        if earr is None:
            return
        for handler in earr:
            handler(event)
        event.mark_complete()

    @classmethod
    def handler_exists(cls, etype, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = cls.__event_map[etype]
        if handler in earr:
            return True
        else:
            return False

    @classmethod
    def custom_handler_exists(cls, ename, handler):
        assert ename is str
        assert type(handler) is Handler
        earr = cls.__custom_event_map.get(ename, None)
        if earr is None:
            return False
        if handler in earr:
            return True
        else:
            return False

