from collections import OrderedDict
parent_indicator = 'parent:'

_parent_indicators = OrderedDict((
    ('p:', 'p'),
    ('parent:', 'parent'),
    ('r:', 'r'),
    ('root:', 'root'),
))


def parent_config_str_splitter(text: str):
    if text.startswith(parent_indicator):
        from_parent = True
        res = (from_parent, text[len(parent_indicator):])
    else:
        from_parent = False
        res = (from_parent, text)
    return res
