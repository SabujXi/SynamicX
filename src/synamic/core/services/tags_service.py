"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

from synamic.core.new_parsers.document_parser import FieldParser, Field
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.classes.path_tree import ContentPath2

#  id or
#  slug ???
import re


class Tag:
    """
    Tags are flat, so remember that only the first part will be taken, others will be left untouched.
    """
    def __init__(self, title=None, slug=None, description=None, others=None):
        assert title is not None
        self.__title = title
        self.__title_lower = title.lower()
        self.__description = description if description is not None else ''
        self.__other_fields = {} if others is None else others  # a flat dictionary

        self.__slug = slug

        if slug is not None:
            slug = re.sub(r'[^a-z0-9+._-]', '-', title, flags=re.I)
            self.__slug = slug
        # print(self)
        # print(repr(self))

    @property
    def title(self):
        return self.__title

    @property
    def slug(self):
        return self.__slug

    @property
    def description(self):
        return self.__description

    def __getitem__(self, item):
        return self.__other_fields.get(item, None)

    # def __getattr__(self, item):
    #     return self.__other_fields.get(item, None)

    def __str__(self):
        return self.__title

    def __repr__(self):
        # print("REPR: %s" % self.title)
        return repr(self.__str__())

    def __eq__(self, other):
        return self.__title.lower() == other.title.lower()

    def __hash__(self):
        return hash(self.__title)


class TagsService:
    def __init__(self, synamic_config):
        self.__config = synamic_config
        self.__tags_by_slug = {}
        self.__tags_by_title_lower = {}
        self.__is_loaded = False

        self.__service_home_path = None
        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self) -> ContentPath2:
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('meta', 'tags'))
        return self.__service_home_path

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
                    # print(root_tags)

                    for tag_field in root_tags.get_multi('tag'):
                        tag_dict = tag_field.to_dict_ordinary()
                        # print(tag_dict)

                        title = tag_dict.get('title', None)
                        if title is not None:
                            del tag_dict['title']

                        id = tag_field.get('id', None)
                        if id is not None:
                            del tag_dict['id']

                        description = tag_field.get('description', None)
                        if description is not None:
                            del tag_dict['description']
                        if title is None:
                            # skip this tag
                            continue
                        # assert id is not None and title is not None, "Tag id must exist"
                        self.add_tag(title, slug=id, description=description, others=tag_dict)
        # for x in self.all:
        #     print(x)
        self.__is_loaded = True

    @property
    def all(self):
        return tuple(self.__tags_by_title_lower.values())

    def add_tag(self, title, slug=None, description=None, others=None):
        t = self.get_tag_by_title(title)
        if t:
            return t
        if self.get_tag_by_title(title):
            return None
        tag = Tag(
            title=title,
            slug=slug,
            description=description,
            others=others
        )

        if slug is not None:
            assert slug not in self.__tags_by_slug, "Duplicate tag id: %s" % slug
            self.__tags_by_slug[tag.slug] = tag
        self.__tags_by_title_lower[tag.title.lower()] = tag
        return tag

    def get_or_add_tag(self, title):  #  by title
        tag = self.get_tag_by_title(title)
        if tag is not None:
            return tag
        else:
            return self.add_tag(title)

    def get_tag_by_title(self, title):
        return self.__tags_by_title_lower.get(title.lower(), None)
    get_tag = get_tag_by_title
    get = get_tag_by_title

    def __getitem__(self, key):
        return self.__tags_by_slug.get(key)

    def __iter__(self):
        return iter(self.all)
