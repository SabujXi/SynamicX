from synamic.frontmatter import parse_front_matter

class Text:
    def __init__(self, body, raw_front):
        self.body = body
        self._raw_frontmatter = raw_front
        self.front_matter_items = {}

def parse_text():
    pass

