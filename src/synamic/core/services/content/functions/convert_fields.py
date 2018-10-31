from collections import OrderedDict


def content_convert_fields(site, model, doc):
    _fields = OrderedDict()
    _field_converters = OrderedDict()

    def content_fields_visitor(a_field, field_path, _res_map_: OrderedDict):
        """
        :param a_field:
        :param field_path: is a tuple of nested field names
        """
        dotted_field = ".".join([field for field in field_path])

        if dotted_field in {'pagination', 'slug', 'permalink', 'chapters'}:
            # skip them
            proceed = True
            return proceed

        field_config = model.get(dotted_field, None)

        if field_config is None:
            # deliver the raw sting to the field
            # assert model_field is not None, "field `%s` is not defined in the model" % dotted_field
            type_name = 'text'
            converter = site.type_system.get_converter(type_name)
            converted_value = converter(a_field.value, site)
        else:
            converter = field_config.converter
            converted_value = converter(a_field.value, site)

        _res_map_[dotted_field] = converted_value
        _field_converters[dotted_field] = converter
        proceed = True
        return proceed

    doc.root_field.visit(content_fields_visitor, _fields)
    return _fields, _field_converters
