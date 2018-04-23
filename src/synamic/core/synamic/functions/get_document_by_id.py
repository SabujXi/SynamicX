from synamic.core.synamic._synamic_enums import Key
from synamic.core.classes.utils import DictUtils


def synamic_get_document_by_id(synamic, mod_name, doc_id):
    self = synamic

    parent_d = self.__content_map[Key.CONTENTS_BY_ID]
    d = DictUtils.get_or_create_dict(parent_d, mod_name)
    assert doc_id in d, "Content id does not exist %s:%s" % (mod_name, d)
    return d[doc_id]
