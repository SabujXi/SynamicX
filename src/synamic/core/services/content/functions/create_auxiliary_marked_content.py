from synamic.core.services.content.marked_content import MarkedContentImplementation
from synamic.core.contracts import ContentContract


def content_create_auxiliary_marked_content(synamic, content, position):
    new_url = content.url_object.join("_/%s/" % position)

    return MarkedContentImplementation(synamic,
                                       content.path_object,
                                       new_url,
                                       content.body,
                                       content.fields,
                                       document_type=ContentContract.__document_types.AUXILIARY)