import enum

"""
* No event for path module loading.
* No event for instantiation
*   for example you are instantiating content/template/etc. module/service/etc., you cannot get/trigger event for this
*   because instantiation is the best place to register events without worrying whether the event being registered
*   is related to another module/service/etc. that need to be loaded before or after.
"""


@enum.unique
class EventTypes(enum.Enum):
    """
    These are all system events - not custom events.
    """

    SETTINGS_PRE_LOAD = 1
    SETTINGS_POST_LOAD = 2

    STATIC_CONTEND_ADDED = 3
    DYNAMIC_CONTENT_ADDED = 4

    # pre service/module load
    TEMPLATE_PRE_LOAD = "TEMPLATE_PRE"
    STATIC_PRE_LOAD = "STATIC_PRE"
    MODEL_PRE_LOAD = "MODEL_PRE"
    CONTENT_PRE_LOAD = "CONTENT_SERVICE_PRE"
    MENU_PRE_LOAD = "MENU_PRE"
    TAGS_PRE_LOAD = "TAGS_PRE"
    CATEGORIES_PRE_LOAD = "CATEGORIES_PRE"
    NULL_PRE_LOAD = "NULL_PRE"

    # post service/module load
    TEMPLATE_POST_LOAD = "TEMPLATE_POST"
    STATIC_POST_LOAD = "STATIC_POST"
    MODEL_POST_LOAD = "MODEL_POST"
    CONTENT_POST_LOAD = "CONTENT_SERVICE_POST"
    MENU_POST_LOAD = "MENU_POST"
    TAGS_POST_LOAD = "TAGS_POST"
    CATEGORIES_POST_LOAD = "CATEGORIES_POST"
    NULL_POST_LOAD = "NULL_POST"

    # synamic
    SYNAMIC_PRE_INIT = "SYNAMIC_PRE_INIT"
    SYNAMIC_POST_INIT = "SYNAMIC_POST_INIT"
    SYNAMIC_PRE_LOAD = "SYNAMIC_PRE_LOAD"
    SYNAMIC_POST_LOAD = "SYNAMIC_POST_LOAD"

    # STREAM : I guess I will not implement this event.
    STREAM_BEFORE = "STREAM_BEFORE"
    STREAM_AFTER = "STREAM_AFTER"

    # BUILD
    PRE_BUILD = "BUILD_PRE"
    POST_BUILD = "BUILD_POST"

    # SERVE
    PRE_SERVE = "PRE_SERVE"
    POST_SERVE = "POST_SERVE"

    # DEPLOY
    PRE_DEPLOY = "PRE_DEPLOY"
    POST_DEPLOY = "POST_DEPLOY"

    # System
    SYSTEM_PRE_START = "SYSTEM_PRE_START"
    #  no post start
