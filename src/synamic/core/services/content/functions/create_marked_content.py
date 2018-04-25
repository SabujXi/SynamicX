from synamic.core.services.content.functions.convert_fields import content_convert_fields
from synamic.core.parsing_systems.document_parser import DocumentParser
from synamic.core.services.content.chapters import get_chapters
from synamic.core.services.content.functions.construct_url_object import content_construct_url_object
from synamic.core.services.content.marked_content import MarkedContentImplementation
from synamic.core.contracts.content import ContentContract


def content_create_marked_content(synamic, file_path, file_content, content_type=ContentContract.types.DYNAMIC):
    doc = DocumentParser(file_content).parse()
    model = synamic.model_service.get_model(file_path.merged_meta_info.get('model', 'default'))

    ordinary_fields, field_converters = content_convert_fields(synamic, model, doc)

    # convert field
    field_config_4_body = model.get('__body__', None)
    if field_config_4_body is not None:
        body_converter = field_config_4_body.converter
    else:
        body_converter = synamic.type_system.get_converter('markdown')
    body = body_converter(doc.body, synamic)
    #
    # TODO: later make them system field: slug -> _slug, permalink -> _permalink, pagination -> _pagination,
    # chapters -> _chapters; so that user can think that fields have direct one to one mapping with value
    slug_field = doc.root_field.get('slug', None)
    permalink_field = doc.root_field.get('permalink', None)
    pagination_field = doc.root_field.get('pagination', None)
    chapters_field = doc.root_field.get('chapters', None)

    ordinary_fields['__pagination'] = None if pagination_field is None else pagination_field.value
    # ordinary_fields['__chapters'] = None if chapters_field is None else chapters_field.value
    if chapters_field is not None:
        ordinary_fields['chapters'] = get_chapters(synamic, chapters_field)
    else:
        ordinary_fields['chapters'] = None

    for key, value in file_path.merged_meta_info.items():
        if key not in {'slug', 'permalink', 'pagination', 'chapters', 'model'}:
            if key not in ordinary_fields:
                ordinary_fields[key] = value
    #
    url_construction_dict = {
        'slug': None if slug_field is None else slug_field.value,
        'permalink': None if permalink_field is None else permalink_field.value
    }
    #
    url_object = content_construct_url_object(synamic, file_path, url_construction_dict)

    content = MarkedContentImplementation(synamic, file_path, url_object,
                                          body, ordinary_fields,
                                          field_converters=field_converters,
                                          content_type=content_type)
    return content
