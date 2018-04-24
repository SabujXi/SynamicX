from synamic.core.urls.url import ContentUrl
from collections import deque
import re


def content_construct_url_object(synamic, path_object, slug_permalink_dict):
    # if self.__url is None:
    # so, /404.html should not be /404.html/(index.html) - see below.
    # Let's start from the root to make url.
    parent_paths = path_object.parent_paths
    url_comps = deque()

    if parent_paths:
        for path in parent_paths:
            meta_info = path.meta_info
            # permalink gets the first priority - whenever permalink is encountered, all previous calculation
            # is discarded
            pm = meta_info.get('permalink', None)
            sl = meta_info.get('slug', None)
            if pm is not None:
                url_comps.clear()
                url_comps.append(pm)
            elif sl is not None:
                url_comps.append(sl)
            else:
                # dir name will be used as slug when not not permalink, neither slug is defined
                _slug = path.basename + '/'
                url_comps.append(_slug)
                # url_comps.append('')

    pm = slug_permalink_dict.get('permalink', None)
    sl = slug_permalink_dict.get('slug', None)
    by_base_name = False
    last_part = None
    if pm is not None:
        url_comps.clear()
        # url_comps.append(pm)
        last_part = pm
    elif sl is not None:
        # url_comps.append(sl)
        last_part = sl
    else:
        # dir name will be used as slug when not not permalink, neither slug is defined
        by_base_name = True
        last_part = path_object.basename
        # url_comps.append()

    _ext_match = re.match(r'(?P<file_name>.*)\.[a-z0-9]+$', last_part, re.I)
    if not _ext_match:
        if not last_part.endswith('/'):
            last_part += '/'
    else:
        if by_base_name:
            fn = _ext_match.group('file_name')
            if fn:
                last_part = fn + '/'

    url_comps.append(last_part)
    cnt_url = ContentUrl(synamic, '')

    for url_path_comp in url_comps:
        cnt_url = cnt_url.join(url_path_comp)  # append_slash=append_slash)
    # print("URL: `%s`" % cnt_url)
    return cnt_url
