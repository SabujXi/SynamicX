from synamic.core.synamic._synamic_enums import Key


def synamic_add_auxiliary_content(synamic, document, content_map):
    self = synamic
    assert document.is_generated_binary_document is True
    # 3. Content Url Object
    assert document.curl not in content_map[
        Key.CONTENTS_BY_CONTENT_URL], "Path %s in content map" % document.curl.path_as_str
    content_map[Key.CONTENTS_BY_CONTENT_URL][document.curl] = document

    # 4. Contents set
    content_map[Key.CONTENTS_SET].add(document)
