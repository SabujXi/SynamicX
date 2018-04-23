from synamic.core.synamic._synamic_enums import Key


def synamic_add_auxiliary_content(synamic, document, content_map):
    self = synamic
    assert document.is_auxiliary is True
    # 3. Content Url Object
    assert document.url_object not in content_map[
        Key.CONTENTS_BY_CONTENT_URL], "Path %s in content map" % document.url_object.path
    content_map[Key.CONTENTS_BY_CONTENT_URL][document.url_object] = document

    # 4. Contents set
    content_map[Key.CONTENTS_SET].add(document)
