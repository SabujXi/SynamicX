"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

#  id or
#  slug ???
from synamic.core.services.tags.functions.construct_tag_url import construct_tag_url
from synamic.core.services.tags.functions.normalize_tag_title import normalize_tag_title
from synamic.core.services.tags.functions.construct_tag_id import construct_tag_id
from synamic.core.parsing_systems.document_parser import FieldParser
from synamic.core.standalones.functions.decorators import not_loaded, loaded


class Tag:
    """
    Tags are flat, so remember that only the first part will be taken, others will be left untouched.
    """
    def __init__(self, synamic, title, id=None, description=None, others=None):
        assert title is not None
        # remove multiple consecutive spaces with one space
        self.__title = normalize_tag_title(title)
        self.__title_lower = self.__title.lower()
        self.__description = description if description is not None else ''
        self.__other_fields = {} if others is None else others  # a flat dictionary
        self.__id = construct_tag_id(id, self.__title_lower)
        self.__synamic = synamic
        self.__url_object = construct_tag_url(synamic, self)

    @property
    def title(self):
        return self.__title

    @property
    def id(self):
        return self.__id

    @property
    def description(self):
        return self.__description

    @property
    def url_object(self):
        return self.__url_object

    def __getitem__(self, item):
        return self.__other_fields.get(item, None)

    def __str__(self):
        return self.__title

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        return self.__id == other.id

    def __hash__(self):
        return hash(self.__id)


class TagsService:
    def __init__(self, synamic):
        self.__synamic = synamic
        self.__tags_by_id = {}
        self.__tags_by_title_lower = {}
        self.__is_loaded = False

        self.__tags_dir = self.__synamic.default_configs.get('dirs')['metas.tags']

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        file_paths = self.service_home_path.list_files()

        for file_path in file_paths:
            if file_path.basename.endswith('.tags.txt') and len(file_path.basename) > len('.tags.txt'):
                with file_path.open('r', encoding='utf-8') as f:
                    model_txt = f.read()
                    root_tags = FieldParser(model_txt).parse()

                    for tag_field in root_tags.get_multi('tag'):
                        tag_dict = tag_field.to_dict_ordinary()

                        title = tag_dict.get('title', None)
                        if title is not None:
                            del tag_dict['title']

                        id = tag_dict.get('id', None)
                        if id is not None:
                            del tag_dict['id']

                        description = tag_field.get('description', None)
                        if description is not None:
                            del tag_dict['description']
                        if title is None:
                            # skip this tag
                            continue
                        # assert id is not None and title is not None, "Tag id must exist"
                        self.add_tag(title, id, description=description, others=tag_dict)
        self.__is_loaded = True

    @loaded
    def reload(self):
        self.__is_loaded = False
        self.load()

    @property
    def all(self):
        return tuple(self.__tags_by_title_lower.values())

    def add_tag(self, title, id=None, description=None, others=None):
        t = self.get_tag_by_title(title)
        if t:
            return t
        if self.get_tag_by_title(title):
            return None
        tag = Tag(
            self.__synamic,
            title,
            id,
            description=description,
            others=others
        )

        assert tag.id not in self.__tags_by_id, "Duplicate tag id: %s" % id
        self.__tags_by_id[tag.id] = tag
        self.__tags_by_title_lower[tag.title.lower()] = tag
        return tag

    def get_or_add_tag(self, title):  # by title
        tag = self.get_tag_by_title(title)
        if tag is not None:
            return tag
        else:
            return self.add_tag(title)

    def get_tag_by_title(self, title):
        return self.__tags_by_title_lower.get(normalize_tag_title(title).lower(), None)
    get_tag = get_tag_by_title
    get = get_tag_by_title

    def __getitem__(self, key):
        return self.__tags_by_id.get(key)

    def __iter__(self):
        return iter(self.get_sorted_tags())

    def get_sorted_tags(self, reverse=False):
        # sorts alphabetically
        tags = self.all
        sorted_tags = sorted(tags, key=lambda tag: tag.title, reverse=reverse)
        return sorted_tags

