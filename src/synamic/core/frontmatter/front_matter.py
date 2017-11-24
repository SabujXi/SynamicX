import re
from ruamel.yaml import YAML
yaml = YAML(typ="safe")

start_pattern = re.compile(r"^\s*(-{3,})[\n\r]+", re.IGNORECASE|re.DOTALL)
end_pattern = re.compile(r"[\n\r]+(-{3,})[\n\r]+", re.IGNORECASE|re.DOTALL)


def parse_front_matter(text):
    status = True
    front = ""
    body = ""
    start_match = start_pattern.search(text)
    if start_match:
        end_match = end_pattern.search(text, start_match.end())
        if end_match:
            body = text[end_match.end():]
            front = text[start_match.end(): end_match.start()]
        else:
            status = None  # None means, the front matter is corrupted
    else:
        status = False
        body = text

    return status, front, body
    # return {"status": status, "front": front, "body": body}


class Document(object):
    def __init__(self, string):
        self.__string = string
        self.__front_text = ""
        self.__body_text = ""
        self.__front_map = None
        self.__has_front_matter = False
        self.__is_front_matter_valid = False

        # parse it
        status, front, body = parse_front_matter(self.__string)
        if status is None:
            self.__has_front_matter = True
            self.__is_front_matter_valid = False
        elif status is False:
            self.__has_front_matter = False
            self.__is_front_matter_valid = False
        else:
            self.__has_front_matter = True
            self.__is_front_matter_valid = True

        self.__front_text = front
        self.__body_text = body

    @property
    def is_front_matter_valid(self):
        return self.__is_front_matter_valid

    @property
    def has_front_matter(self):
        return self.__has_front_matter

    @property
    def has_valid_front_matter(self):
        return self.has_front_matter and self.is_front_matter_valid

    @property
    def raw_front_matter(self):
        return self.__front_text

    @property
    def front_map(self):
        fm = self.__front_map
        if not fm:
            fm = self.__front_map = yaml.load(self.raw_front_matter)
        return fm

    @property
    def body(self):
        return self.__body_text


