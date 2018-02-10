"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import enum
import re
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.functions.normalizers import normalize_key, normalize_keys
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.contracts.module import BaseMetaModuleContract
from synamic.core.contracts.content import ContentContract


class TaxonomyTerm:
    @enum.unique
    class types(enum.Enum):
        SINGLE = 'single'
        MULTIPLE = 'multiple'
        HIERARCHICAL = 'hierarchical'

    type_values = [x.value for x in types]

    def __init__(self, module, taxonomy_type, taxonomy_term, term_map):
        term_map = normalize_keys(term_map)

        assert isinstance(taxonomy_type, self.types), "taxonomy type must be a member of enum called TaxonomyTerm"

        self.__module = module
        self.__taxonomy_type = taxonomy_type
        self.__taxonomy_term = taxonomy_term
        self.__term_map = term_map

        self.__title = term_map.get('title')
        assert self.__title
        # Slug is not needed, id will serve the purpose
        self.__id_ = term_map.get('id', None)
        # assert self.__id_
        self.__description = term_map.get('description', '')
        self.__parent = term_map.get('parent', None)
        if self.__parent is not None:
            if self.__taxonomy_type is not self.types.HIERARCHICAL:
                raise Exception('Non-hierarchical terms cannot have parent')

        self.__contents = set()

    def add_content(self, content):
        assert isinstance(content, ContentContract), "Only valid contents can be added - those who are implementing ContentContract"
        self.__contents.add(content)

    @property
    def term(self):
        return self.__taxonomy_term

    @property
    def type(self):
        return self.__taxonomy_type

    @property
    def title(self):
        return self.__title

    @property
    def title_normalized(self):
        # TODO: put some logic here
        return self.__title

    @property
    def id(self):
        return self.__id_

    @property
    def description(self):
        return self.__description

    @property
    def parent(self):
        if self.parent_id is None:
            return None
        return self.__module.get_term_parent(self)

    @property
    def parent_id(self):
        return self.__parent

    def __repr__(self):
        return str(self.__term_map)

    def __str__(self):
        return self.title


class TaxonomyPage(ContentContract):

    @property
    def module_object(self):
        return self.__module

    @property
    def path_object(self):
        return self.__path

    @property
    def content_id(self):
        return None

    def get_stream(self):
        super().get_stream()

    @property
    def config(self):
        return self.__config

    @property
    def is_dynamic(self):
        return True

    @property
    def is_static(self):
        return False

    @property
    def is_auxiliary(self):
        return False

    @property
    def content_type(self):
        return self.types.DYNAMIC

    @property
    def mime_type(self):
        return 'text/html'


class TaxonomyModule(BaseMetaModuleContract):
    def __init__(self, config):
        self.__config = config
        # self.__taxonomies_by_type = {}
        self.__terms_map = {}
        self.__terms = set()
        self.__term_vs_taxonomy_type_map = {}
        self.__is_loaded = False

    @property
    def taxonomy_wrapper(self):
        return TaxonomyModuleWrapper(self)

    @not_loaded
    def load(self):
        dirs, _files = self.__config.path_tree.get_module_paths(self, directories_only=True, depth=1)
        dir_bases = [path.basename for path in dirs]
        typs = []
        for dir_base in dir_bases:
            dir_base = dir_base.lower()
            if dir_base not in TaxonomyTerm.type_values:
                raise Exception('Invalid taxonomy type: %s where values are: %s' % (dir_base, TaxonomyTerm.type_values))
            else:
                if dir_base == TaxonomyTerm.types.SINGLE.value:
                    typs.append((dir_base, TaxonomyTerm.types.SINGLE))
                elif dir_base == TaxonomyTerm.types.MULTIPLE.value:
                    typs.append((dir_base, TaxonomyTerm.types.MULTIPLE))
                else:
                    assert dir_base == TaxonomyTerm.types.HIERARCHICAL.value
                    typs.append((dir_base, TaxonomyTerm.types.HIERARCHICAL))

        taxonomy_terms = set()

        for dir_base, typ in typs:
            typ_taxonomies_paths, _fls = self.__config.path_tree.get_module_paths(self, starting_comps=(dir_base,), directories_only=True, depth=1)
            typ_taxonomies = [path.basename for path in typ_taxonomies_paths]

            # self.__taxonomies_by_type[typ] = {}

            for term in typ_taxonomies:
                assert term not in self.__terms_map, "Duplicate term detected: %s" % term
                self.__terms_map[term] = {
                    'by_id': {},
                    'by_title_normalized': {}
                }

                self.__term_vs_taxonomy_type_map[term] = typ

                if term in taxonomy_terms:
                    raise Exception("Multiple taxonomy terms with the same name detected: %s" % term)
                _dir_paths_, file_paths = self.__config.path_tree.get_module_paths(self, starting_comps=(dir_base, term), files_only=True)
                for file_path in file_paths:
                    with self.__config.path_tree.open(file_path.absolute_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        py_obj = load_yaml(text)
                        assert type(py_obj) is list
                        for term_map in py_obj:
                            assert type(term_map) is dict
                            term_obj = TaxonomyTerm(self, typ, term, term_map)
                            self.add_term(term_obj)
        self.__is_loaded = True
        for x in self.__terms:
            print("TERM:\n    %s" % x)

    def normalize_title(self, title):
        res = re.sub(r'\t', ' ', title)
        res = re.sub(r'\s{2,}', ' ', res)
        return res

    @property
    def terms(self):
        return self.__terms

    @property
    def terms_map(self):
        return self.__terms_map

    def add_term(self, term_obj):
        if term_obj.id:
            if term_obj.id in self.__terms_map[term_obj.term]['by_id']:
                raise Exception('duplicate id detected')
            else:
                self.__terms_map[term_obj.term]['by_id'][term_obj.id] = term_obj
        if term_obj.title_normalized in self.__terms_map[term_obj.term]['by_title_normalized']:
            raise Exception('Duplicate normalized title detected')
        else:
            self.__terms_map[term_obj.term]['by_title_normalized'][term_obj.title_normalized] = term_obj
        self.__terms.add(term_obj)

    @loaded
    def get_term_parent(self, term_obj):
        parent_id = term_obj.parent_id
        return self.__terms_map[term_obj.term]['by_id'].get(parent_id, None)

    @loaded
    def get_term_by_id(self, term, term_id):
        return self.__terms_map[term]['by_id'].get(term_id, None)

    @loaded
    def get_term_by_title(self, term, title):
        ntitle = self.normalize_title(title)
        return self.__terms_map[term]['by_title_normalized'].get(ntitle, None)

    @loaded
    def get_terms_from_frontmatter(self, key_value_map):
        processed = {}
        unprocessed = {}
        for key, value in key_value_map.items():
            if key in self.__terms_map:
                if value.startswith('@'):
                    term_obj_s = self.get_term_by_id(value.lstrip('@'))
                    if term_obj_s is None:
                        raise Exception("Invalid term id of term %s and id %s" % (key, value))
                else:
                    _taxonomy_type = self.__term_vs_taxonomy_type_map[key]

                    parsed_values = TaxonomyValueParsers.parse(_taxonomy_type, key, value)
                    term_obj_s = []
                    for parsed_value in parsed_values:
                        term_obj = self.get_term_by_title(key, parsed_value)
                        if term_obj is None:
                            term_obj = TaxonomyTerm(self, _taxonomy_type, key, {'title': parsed_value})
                            term_obj_s.append(term_obj)
                            self.add_term(term_obj)
                        else:
                            term_obj_s.append(term_obj)
                    if _taxonomy_type is TaxonomyTerm.types.SINGLE:
                        processed[key] = term_obj_s[0]
                    else:
                        processed[key] = term_obj_s
            else:
                unprocessed[key] = value

        return processed, unprocessed

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def name(self):
        return normalize_key('taxonomy')

    @property
    def config(self):
        return self.__config

    @property
    def dependencies(self):
        return set()


class TaxonomyModuleWrapper:
    def __init__(self, module_):
        self.__module_ = module_
        self.get_term_parent = module_.get_term_parent
        self.get_term_by_id = module_.get_term_by_id
        self.get_term_by_title = module_.get_term_by_title
        self.terms = module_.terms
        self.terms_map = module_.terms_map
        self.get_terms_from_frontmatter = module_.get_terms_from_frontmatter


class TaxonomyValueParsers:
    _default_values = {
        normalize_key('tags'): [],
        normalize_key('categories'): [],
    }

    @classmethod
    def _generic_multiple_hierarchical_parser(cls, txt):
        txt = txt.strip()
        parts = [x.strip() for x in txt.split(',')]
        return parts

    @classmethod
    def _generic_strip_and_return(cls, txt):
        return [txt.strip()]

    @classmethod
    def _default_value_parsers(cls, term):
        return {
            'tags': cls._generic_multiple_hierarchical_parser,
            'categories': cls._generic_multiple_hierarchical_parser,
        }.get(term, None)

    @classmethod
    def parse(cls, taxonomy_type, term, value):
        if taxonomy_type is TaxonomyTerm.types.SINGLE:
            res = cls._generic_strip_and_return(value)
        else:
            parser = cls._default_value_parsers(term)
            if parser is None:
                res = cls._generic_multiple_hierarchical_parser(value)
            else:
                res = parser(value)
        return res

