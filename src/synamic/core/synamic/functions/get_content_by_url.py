from synamic.core.synamic._synamic_enums import Key
from synamic.core.services.urls.url import ContentUrl


def synamic_get_content_by_url(synamic, curl: ContentUrl, content_map):
    self = synamic
    assert type(curl) is ContentUrl
    if curl in content_map[Key.CONTENTS_BY_CONTENT_URL]:
        cont = content_map[Key.CONTENTS_BY_CONTENT_URL][curl]
    else:
        cont = None
    return cont
