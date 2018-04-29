parent_indicator = 'parent:'


def parent_config_str_splitter(text: str):
    if text.startswith(parent_indicator):
        from_parent = True
        res = (from_parent, text[len(parent_indicator)-1:])
    else:
        from_parent = False
        res = (from_parent, text)
    return res
