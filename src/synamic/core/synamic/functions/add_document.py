from synamic.core.synamic._synamic_enums import Key


def synamic_add_document(synamic, document, content_map):
    self = synamic
    assert document.is_auxiliary is False
    # 1. Content id
    if document.id is not None and document.id != "":
        parent_d = content_map[Key.CONTENTS_BY_ID]
        # d = DictUtils.get_or_create_dict(parent_d, mod_name)

        assert document.id not in parent_d, \
            "Duplicate content id cannot exist %s" % document.id
        parent_d[document.id] = document

    # 2. Normalized relative file path
    if document.path_object is not None:
        _path = document.path_object.norm_relative_path
        parent_d = content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
        assert _path not in parent_d, "Duplicate normalized relative file path: %s" % _path
        parent_d[_path] = document

    # 3. Content Url Object
    assert document.url_object not in content_map[
        Key.CONTENTS_BY_CONTENT_URL], "Path %s in content map" % document.url_object.path
    content_map[Key.CONTENTS_BY_CONTENT_URL][document.url_object] = document

    # 4. Contents set
    content_map[Key.CONTENTS_SET].add(document)

    if document.is_dynamic:
        content_map[Key.DYNAMIC_CONTENTS].add(document)
