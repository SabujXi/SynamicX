import os
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_file_contents(fn):
    full_fn = os.path.join(_BASE_DIR, fn)
    with open(full_fn, encoding='utf-8') as f:
        text = f.read()
    return text
