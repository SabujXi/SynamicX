import enum
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.functions.normalizers import normalize_key, normalize_keys
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.contracts.module import BaseMetaModuleContract


class TaxonomyTerm:
    @enum.unique
    class types(enum.Enum):
        SINGLE = 'single'
        MULTIPLE = 'multiple'
        HIERARCHICAL = 'hierarchical'

    type_values = [x.value for x in types]

    def __init__(self, module, taxonomy_type, taxonomy_term, term_map):
        term_map = normalize_keys(term_map)

        self.__module = module
        self.__taxonomy_type = taxonomy_type
        self.__taxonomy_term = taxonomy_term
        self.__term_map = term_map

        self.__title = term_map.get('title')
        assert self.__title
        # Slug is not needed, id will serve the purpose
        self.__id_ = term_map.get('id')
        assert self.__id_
        self.__description = term_map.get('description', '')
        self.__parent = term_map.get('parent', None)

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

    def __str__(self):
        return str(self.__term_map)


class TaxonomyModule(BaseMetaModuleContract):
    def __init__(self, config):
        self.__config = config
        self.__term_map = {}
        self.__terms = set()
        self.__is_loaded = False

    @property
    @loaded
    def taxonomy_wrapper(self):
        return TaxonomyModuleWrapper(self.__terms)

    @not_loaded
    def load(self):
        dirs, _files = self.__config.path_tree.get_module_paths(self, directories_only=True, depth=1)
        typs = [path.basename for path in dirs]
        for typ in typs:
            if typ not in TaxonomyTerm.type_values:
                raise Exception('Invalid taxonomy type: %s where values are: %s' % (typ, TaxonomyTerm.type_values))
        taxonomy_terms = set()
        for typ in typs:
            typ_taxonomies_paths, _fls = self.__config.path_tree.get_module_paths(self, starting_comps=(typ,), directories_only=True, depth=1)
            typ_taxonomies = [path.basename for path in typ_taxonomies_paths]

            self.__term_map[typ] = {}

            for term in typ_taxonomies:
                assert term not in self.__term_map, "Duplicate term detected: %s" % term
                self.__term_map[typ][term] = {
                    'by_id': {},
                    'by_title_normalized': {}
                }

                if term in taxonomy_terms:
                    raise Exception("Multiple taxonomy terms with the same name detected: %s" % term)
                _dir_paths_, file_paths = self.__config.path_tree.get_module_paths(self, starting_comps=(typ, term), files_only=True)
                for file_path in file_paths:
                    with self.__config.path_tree.open_file(file_path.absolute_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        py_obj = load_yaml(text)
                        assert type(py_obj) is list
                        for term_map in py_obj:
                            assert type(term_map) is dict
                            """
                            -
                              title: C
                              id: code-c
                              description: Nothing
                            -
                              title: C++
                              id: code-cpp
                              description: Nothing
                              parent: '@code-c'
                            """
                            term_obj = TaxonomyTerm(self, typ, term, term_map)
                            if term_obj.id in self.__term_map[term_obj.type][term]['by_id']:
                                raise Exception('duplicate id detected')
                            else:
                                self.__term_map[term_obj.type][term][term_obj.id] = term_obj
                            if term_obj.title_normalized in self.__term_map[term_obj.type][term]['by_title_normalized']:
                                raise Exception('A normalized title already exist: %s' % term_obj.title_normalized)
                            else:
                                self.__term_map[term_obj.type][term]['by_title_normalized'][term_obj.title_normalized] = term_obj
                            self.__terms.add(term_obj)
        self.__is_loaded = True
        for x in self.__terms:
            print("TERM:\n    %s" % x)

    def get_term_parent(self, term_obj):
        parent_id = term_obj.parent_id
        return self.__term_map[term_obj.type][term_obj.term]['by_id'][parent_id]

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
    def __init__(self, terms):
        self.__terms = terms

    def __contains__(self, item):
        normalize_key(item)

    def __getitem__(self, item):
        normalize_key(item)

    def get(self, default=None):
        pass
