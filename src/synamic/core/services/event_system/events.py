from synamic.core.services.event_system.event_types import EventTypes
from synamic.exceptions.synamic_exceptions import LogicalError


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


# DONE: Event system must not be class based, instead an event system must be instantiated as we may have
# multiple copy of synamic in the same process.
# also, it is needed for synamic.reload()

class EventSystem:
    """
    Handler config:
    handler(what)
    e.g.:
        what: site obj, content service/module object, etc.
        
    Custom event handlers are primarily for external plugins. So, anyone is can trigger that.
    BUT, system events (EventTypes) are only for site and only site can trigger that.
    So, as a protection only the first time the trigger method can be achieved and any subsequent call will raise
    exception.
    
    * System event __document_types can be derived from the EventTypes enum, but custom event __document_types are specified by string.
    The strings are lowercased to avoid any type of probable conflict from inexperienced users/plugin-developers.
    
    Handler functions will be called with an event object. An event object will hold a subject,
    and a map of other objects where strings are used as keys.
    
    """

    # a site/config cannot possess or create more than one event system.
    __instances_map = {}

    @classmethod
    def get_event_system(cls, site):
        # return cls.__instances_map.get(site, None)
        raise NotImplemented

    def __init__(self, site_or_synamic):
        assert site_or_synamic not in self.__instances_map
        self.__instances_map[site_or_synamic] = self
        #  event maps: key => event type, value => ordered dict of event handlers
        self.__get_trigger_count = 0
        self.__event_map = {}
        self.__custom_event_map = {}

        # will use the following when an int will be used to cancel a registered event
        self.__last_event_id = 0
        self.__last_custom_event_id = 0

        for et in EventTypes:
            self.__event_map[et] = []

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def add_event_handler(self, etype: EventTypes, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = self.__event_map[etype]
        earr.append(handler)

    def add_custom_event_handler(self, ename, handler):
        assert type(ename) is str
        assert type(handler) is Handler
        ename = ename.lower()
        earr = self.__event_map.get(ename, None)
        if earr is None:
            earr = self.__event_map[ename] = []
        earr.append(handler)

    def remove_event_handler(self, etype, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = self.__event_map[etype]
        earr.remove(handler)

    def remove_custom_event_handler(self, ename, handler):
        assert type(ename) is str
        assert type(handler) is Handler
        ename = ename.lower()
        earr = self.__event_map.get(ename, None)
        if earr is None:
            earr = self.__event_map[ename] = []
        earr.remove(handler)

    def __trigger_event(self, etype, event):
        assert type(etype) is EventTypes
        assert type(event) is Event
        earr = self.__event_map[etype]
        for handler in earr:
            handler(event)

    def _get_trigger(self):
        if self.__get_trigger_count == 0:
            return self.__trigger_event
        raise LogicalError("_get_trigger can only be used by site itself. Do not try to get it after site got it."
                        "We are protecting it.")

    def trigger_custom_event(self, ename, event):
        assert ename is None
        assert type(event) is Event
        ename = ename.lower()
        earr = self.__custom_event_map[ename]
        if earr is None:
            return
        for handler in earr:
            handler(event)
        event.mark_complete()

    def handler_exists(self, etype, handler):
        assert type(etype) is EventTypes
        assert type(handler) is Handler
        earr = self.__event_map[etype]
        if handler in earr:
            return True
        else:
            return False

    def custom_handler_exists(self, ename, handler):
        assert ename is str
        assert type(handler) is Handler
        earr = self.__custom_event_map.get(ename, None)
        if earr is None:
            return False
        if handler in earr:
            return True
        else:
            return False

