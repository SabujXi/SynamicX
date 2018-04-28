from synamic.core.synamic.functions.get_content import synamic_get_content
from synamic.core.exceptions.synamic_exceptions import GetUrlFailed, GetContentFailed


def synamic_get_url(synamic, parameter, content_map):
    try:
        cnt = synamic_get_content(synamic, parameter, content_map)
    except GetContentFailed:
        # Should raise exception or just return None/False
        raise GetUrlFailed("Url could not be found for: %s" % parameter)
    return cnt.url_object.path
