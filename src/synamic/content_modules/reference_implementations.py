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

_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class MarkedContentImplementation(MarkedDocumentContract):
    def __init__(self, config, module_object, path_object, file_content: str):
        self.__config = config
        self.__module = module_object
        self.__path = path_object

        self.__content_type = ContentContract.types.DYNAMIC
        self.__file_content = file_content
        self.__pagination = None

        self.__front_text = ""
        self.__body_text = ""
        self.__frontmatter = None
        self.__has_front_matter = False
        self.__is_front_matter_valid = False

        # parse it
        status, front, body = parse_front_matter(self.__file_content)
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

        # doc properties
        self.__title = None
        self.__url = None
        self.__created_on = None
        self.__updated_on = None
        self.__summary = None
        self.__tags = None
        self.__categories = None
        self.__body = None

        # terms
        self.__terms = set()

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
        return self.frontmatter.get('id', None)

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

    def _set_auxiliary(self):
        assert self.__content_type is ContentContract.types.DYNAMIC, "The content type of text content is initially dynamic"
        self.__content_type = ContentContract.types.AUXILIARY

    def create_auxiliary(self, prefix, serial):
        auxiliary_clone = self.__class__(self.__config, self.__module, self.__path, self.__file_content)
        auxiliary_clone._set_auxiliary()
        auxiliary_clone.url_object = self.url_object.create_auxiliary_url(prefix, serial)
        return auxiliary_clone

    @property
    def is_frontmatter_valid(self):
        return self.__is_front_matter_valid

    @property
    def has_frontmatter(self):
        return self.__has_front_matter

    @property
    def has_valid_frontmatter(self):
        return self.has_frontmatter and self.is_frontmatter_valid

    @property
    def raw_frontmatter(self):
        return self.__front_text

    @property
    def frontmatter(self):
        if not self.__frontmatter:
            self.__frontmatter = Frontmatter(self.__config, load_yaml(self.raw_frontmatter))
        return self.__frontmatter

    @property
    def body(self):
        if self.__body is None:
            self.__body = Markup(render_markdown(self.__config, self.__body_text))
        return self.__body

    @property
    def title(self):
        return self.frontmatter.get("title", None)

    @property
    def url_object(self):
        return self.__url

    @url_object.setter
    def url_object(self, url_object):
        assert self.__url is None
        self.__url = url_object

    @property
    def absolute_url(self):
        return self.url_object.full_url

    @property
    def created_on(self):
        return self.frontmatter.get('created-on', None)

    @property
    def updated_on(self):
        updt = self.frontmatter.get('updated-on')
        if not updt:
            updt = self.created_on
        return updt

    @property
    def summary(self):
        if self.__summary is None:
            sum_ = self.frontmatter.get('summary', None)
            if sum_ is None or sum_.strip() == '':
                char_count = 200
                res_txt = self.body.striptags()
                if len(res_txt) < char_count:
                    char_count = len(res_txt)
                sum_ = res_txt[:char_count]
            self.__summary = sum_
        return self.__summary

    @property
    def terms(self):
        if self.__terms is None:
            tx = self.__config.taxonomy
            # TODO: fix this
            #  terms_map
        return self.__terms

    @property
    def tags(self):
        return self.frontmatter.terms.get('tags', [])

    @property
    def categories(self):
        return self.frontmatter.terms.get('categories', [])

    @property
    def template_name(self):
        res = self.frontmatter.get('template', None)
        return res.template_name

    @property
    def template_module_object(self):
        res = self.frontmatter.get('template', None)
        mod_name = res.module_name
        return self.__config.get_module(mod_name)

    def trigger_pagination(self):
        rules_txt = self.frontmatter.get('pagination-filter', None)
        if rules_txt:
            print("\n Rules txt:")
            print(rules_txt)
            print()
            per_page = self.frontmatter.get('pagination-content-per-page', None)
            if not per_page:
                per_page = 2  # later we will take the default from config

            starting_content = self

            pg_stream = PaginationStream(self.__config, starting_content, rules_txt, per_page)
            print(">>>>>>\nAuxiliary contents:")
            print(pg_stream.auxiliary_contents)
            print("\n")
            return pg_stream.auxiliary_contents
        else:
            return tuple()

    @property
    def pagination(self):
        return self.__pagination

    @pagination.setter
    def pagination(self, pg):
        assert self.__pagination is None and pg is not None
        self.__pagination = pg

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

    @property
    def title(self):
        return self.__content.title

    @property
    def name(self):
        return self.__content.content_name

    @property
    def id(self):
        return self.__content.content_id

    @property
    def frontmatter(self):
        return self.__content.frontmatter

    @property
    def body(self):
        return self.__content.body

    @property
    def created_on(self):
        return self.__content.created_on

    @property
    def updated_on(self):
        return self.__content.updated_on

    @property
    def url_path(self):
        return self.__content.url_object.path

    # 'absolute_url': self.absolute_url,  TODO: Fix error

    @property
    def tags(self):
        return self.__content.tags

    @property
    def categories(self):
        return self.__content.categories

    @property
    def summary(self):
        return self.__content.summary

    @property
    def pagination(self):
        return self.__content.pagination

    def __str__(self):
        return {
            'title': self.title,
            'name': self.name,
            'id': self.id,
            'frontmatter': self.frontmatter,
            'body': self.body,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'url_path': self.url_path,
            # 'absolute_url': self.absolute_url,  TODO: Fix error
            'tags': self.tags,
            'categories': self.categories,
            'pagination': self.pagination
        }


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
        dynamic_contents = set()
        static_contents = set()

        for file_path in paths:
            if file_path.extension.lower() in {'md', 'markdown'}:
                with self.__config.path_tree.open_file(file_path.relative_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    content_obj = self.content_class(self.__config, self, file_path, text)
                    content_obj.url_object = self._create_url_object(content_obj.frontmatter)

                    if not content_obj.has_valid_frontmatter:
                        raise Exception("Front matter is corrupted or invalid")
                    if content_obj.content_id in self.__dynamic_contents:
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

