"""

forntmatter_default_values = {
    normalize_key('tags'): [],
    normalize_key('categories'): [],
}


default_value_parsers_map(cls):
    return {
        'tags': cls._tags_categories_parser,
        'categories': cls._tags_categories_parser,
    }
    


    @staticmethod
    def _tags_categories_parser(txt):
        txt = txt.strip()
        parts = [x.strip() for x in txt.split(',')]
        return parts
"""