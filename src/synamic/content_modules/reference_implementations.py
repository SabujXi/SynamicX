import io
import re
import mimetypes
from synamic.core.classes.pagination import PaginationStream
from synamic.core.contracts import BaseContentModuleContract, ContentContract
from synamic.core.contracts.document import MarkedDocumentContract
from synamic.core.functions.decorators import not_loaded, loaded
from synamic.core.functions.frontmatter import parse_front_matter
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.classes.frontmatter import Frontmatter
from synamic.core.classes.url import ContentUrl
from markupsafe import Markup
from synamic.core.functions.normalizers import normalize_key
from synamic.core.functions.md import render_markdown
from synamic.core.classes.mapping import FinalizableDict
from synamic.core.new_parsers.document_parser import DocumentParser

_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class MarkedContentImplementation(MarkedDocumentContract):
    def __init__(self, config, module_object, path_object, file_content: str):
        self.__config = config
        self.__module = module_object
        self.__path = path_object
        self.__content_type = ContentContract.types.DYNAMIC
        self.__file_content = file_content

        self.__body = None
        self.__fields = None

        self.__url = None

        # loading body and field
        doc = DocumentParser(self.__file_content).parse()

        res_map = self.__config.model_service.get_converted('text', doc.root_field, doc.body)
        print("Resp Map : %s" % res_map)
        self.__body = res_map['__body__']
        # del res_map['__body__']
        self.__fields = res_map
        print("Resp Map2: %s" % res_map)

    # temporary for fixing sitemap
    @property
    def config(self):
        return self.__config

    @property
    def module_object(self):
        return self.__module

    @property
    def path_object(self):
        return self.__path

    @property
    def content_id(self):
        return self.fields.get('id', None)

    def get_stream(self):
        template_module, template_name = self.template_module_object, self.template_name
        res = template_module.render(template_name, content=self.get_content_wrapper())
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def content_type(self):
        return self.__content_type

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.url_object.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def body(self):
        return self.__body

    @property
    def fields(self):
        return self.__fields

    @property
    def url_object(self):
        if self.__url is None:
            print("Fields: %s" % self.fields)
            self.__url = ContentUrl(self.__config, self.fields['permalink'])
        return self.__url

    @property
    def absolute_url(self):
        return self.url_object.full_url

    @property
    def template_name(self):
        template_name = self.fields.get('template', None)
        # TODO: later support other template module than synamic template
        return template_name

    @property
    def template_module_object(self):
        # TODO: later support other template module than synamic template
        template_name = self.fields.get('template', None)
        return self.__config.get_module('synamic-template')

    def get_content_wrapper(self):
        # TODO: should place in contract!
        # So, with cotract it can be used in paginator too
        return ContentWrapper(self)

    def __str__(self):
        return self.path_object.relative_path

    def __repr__(self):
        return str(self)


class ContentWrapper:
    __slots__ = ('__content',)

    def __init__(self, content):
        self.__content = content

    def __getattr__(self, item):
        return getattr(self.__content, item)

    @property
    def id(self):
        return self.__content.content_id

    @property
    def url_path(self):
        return self.__content.url_object.path


class MarkedContentModuleImplementation(BaseContentModuleContract):
    __slots__ = ('__config', '__is_loaded', '__contents_by_id', '__dynamic_contents', '__auxiliary_contents')

    def __init__(self, _cfg):
        self.__config = _cfg
        self.__is_loaded = False
        self.__contents_by_id = FinalizableDict()
        self.__dynamic_contents = frozenset()
        self.__static_contents = frozenset()

    @property
    def name(self):
        return normalize_key('reference-marked-content-module')

    @property
    def config(self):
        return self.__config

    @property
    def content_class(self):
        return MarkedContentImplementation

    @property
    def dependencies(self):
        return {"synamic-template"}

    @property
    def is_loaded(self):
        return self.__is_loaded

    def _create_url_object(self, frontmatter):
        is_dir = True
        url_str = frontmatter['permalink']  # need to change to path
        assert not _invalid_url.match(url_str), "url_object cannot have scheme"

        if url_str.endswith('/'):
            is_dir = True
        else:
            if '.' in url_str:
                is_dir = False

        if self.root_url_path:
            url_str += self.root_url_path

        url = ContentUrl(self.__config, url_str, is_dir=is_dir)
        return url

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_file_paths(self)
        print(paths)
        dynamic_contents = set()
        static_contents = set()

        for file_path in paths:
            if file_path.extension.lower() in {'md', 'markdown'}:
                with file_path.open("r", encoding="utf-8") as f:
                    text = f.read()
                    content_obj = self.content_class(self.__config, self, file_path, text)

                    content_id = content_obj.fields.get('id', None)
                    if content_id in self.__dynamic_contents:
                        if content_obj.content_id is not None:
                            raise Exception("Duplicate `{module_name}` content id. It is `{content_id}`".format(module_name=self.name, content_id=content_obj.id))
                        self.__contents_by_id[content_obj.content_id] = content_obj
                    dynamic_contents.add(content_obj)
            else:
                static_content = self.__config.create_static_content(self, file_path)
                static_contents.add(static_content)
        self.__dynamic_contents = frozenset(dynamic_contents)
        self.__static_contents = frozenset(static_contents)
        self.__contents_by_id.finalize()
        self.__is_loaded = True

    @property
    def root_url_path(self):
        return ""

    @property
    @loaded
    def static_contents(self):
        return self.__static_contents

    @property
    @loaded
    def dynamic_contents(self):
        return self.__dynamic_contents

    def get_content_by_id(self, content_id, default=None):
        return self.__contents_by_id.get(content_id, default)

