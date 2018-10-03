import re


def construct_tag_id(tag_id, title_lower):
    if tag_id is None:
        tag_id = re.sub(r'[^a-z0-9+._-]', '-', title_lower, flags=re.I).strip()
    return tag_id
