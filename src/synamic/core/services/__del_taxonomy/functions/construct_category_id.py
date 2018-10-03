import re


def construct_category_id(category_id, title_lower):
    if category_id is None:
        category_id = re.sub(r'[^a-z0-9+._-]', '-', title_lower, flags=re.I).strip()
    return category_id
