import re


def normalize_category_title(title):
    """
    ** it does not LOWER
    """
    return re.sub(r' {2,}', ' ', title, flags=re.I).strip()
