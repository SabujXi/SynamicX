import os

from synamic.core.exceptions.synamic_exceptions import GetContentFailed
from synamic.core.standalones.functions.normalizers import normalize_key
from synamic.core.synamic._synamic_enums import Key


def synamic_get_content(synamic, parameter, content_map):
    """
    Finds a content objects depending on name/content-id/url-path/file-path

    Format:
    <content|static>:<id>|<file-path>:...

    Examples:
        - content:id:it_39
        - content:file:/text-logo.png
        - content:file:text-logo.png
        - static:file:home-logo.png
    """
    self = synamic
    parts = parameter.split(':')
    assert len(parts) == 3, "Invalid geturl/get_content parameter"

    # 1. Into name
    mod_name = normalize_key(parts[0])
    search_type = normalize_key(parts[1])
    search_what = parts[2].strip()
    # print("Search what: %s" % search_what)

    # 4. Content id
    if search_type == normalize_key('id'):
        parent_d = content_map[Key.CONTENTS_BY_ID]
        assert search_what in parent_d, "Content id does not exist %s:%s:%s %s" % (
            mod_name, search_type, search_what, parent_d)
        res = parent_d[search_what]

    # 6. Normalized relative file path
    elif search_type == normalize_key('file'):
        # _search_what = os.path.join(mod_name, search_what)
        _search_what = search_what.lower().lstrip(r'\/')
        if mod_name == 'static':
            _search_what = 'assets/' + mod_name + '/' + _search_what
        else:
            _search_what = mod_name + '/' + _search_what
        _search_what = os.path.join(*self.path_tree.to_cpath_comps(_search_what))

        if mod_name == normalize_key('sass'):
            assert synamic.path_tree.exists('assets/sass/' + search_what), "File not found with the module and name: %s:%s:%s:  " % (
                mod_name, search_type, _search_what)
            res = synamic.sass_service.get_css_content('assets/sass/' + search_what)
        else:
            parent_d = content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            assert _search_what in parent_d, "File not found with the module and name: %s:%s:%s:  " % (
                mod_name, search_type, _search_what)
            res = parent_d[_search_what]
    else:
        # Should raise exception or just return None/False
        raise GetContentFailed("Content could not be found for: %s" % parameter)

    return res
