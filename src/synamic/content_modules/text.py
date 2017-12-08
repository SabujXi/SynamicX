from synamic.core.classes.pagination import PaginationStream
import io
import mimetypes

from synamic.core.contracts import ContentModuleContract, ContentContract
from synamic.core.contracts.document import MarkedDocumentContract
# from synamic.core.classes.document import MarkedDocument
# from synamic.core.synamic_config import SynamicConfig
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.functions.frontmatter import parse_front_matter
import re
from synamic.core.functions.frontmatter import parse_front_matter
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.classes.frontmatter import Frontmatter
from synamic.core.classes.url import ContentUrl
import mistune
from markupsafe import Markup
from synamic.core.functions.normalizers import normalize_key
from synamic.core.functions.md import render_markdown
_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)
"""
Text files must start with a number. The initial zero of the number will be stripped off
A dot will follow the number, a space if optional.
- that is the id part - no two text file can have the same id -
the rest is the file name you want to give to it.
"""


class TextContent(MarkedDocumentContract):
    def __init__(self, config, module_object, path_object, file_content: str):
        # self.__init_document(url_suffix=url_suffix)
        # self.__text_id = text_id
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

    @property
    def module_object(self):
        return self.__module

    @property
    def path_object(self):
        return self.__path

    @property
    def content_name(self):
        return self.frontmatter.get('name')
        # raise NotImplemented

    @property
    def content_id(self):
        return self.frontmatter.get('id', None)
        # return self.module_object.name + ":" + str(self.__text_id)

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

    # def __getitem__(self, item):
    #     return self.frontmatter[item]

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
        return Markup(render_markdown(self.__config, self.__body_text))

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
        return self.frontmatter.get('updated-on')

    @property
    def summary(self):
        return self.frontmatter.get('summary', None)

    @property
    def tags(self):
        return self.frontmatter.get('tags', None)

    @property
    def categories(self):
        return self.frontmatter.get('categories', None)

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
        # print("\n~~~~~~~~~~~~~~~~pagination triggered~~~~~~~~~~~~~\n")
        rules_txt = self.frontmatter.get('pagination-filter', None)
        # print("\n~~~~~~~~~~~~~~~~Rules txt: %s~~~~~~~~~~~~~\n" % rules_txt)
        if rules_txt:
            per_page = self.frontmatter.get('pagination-content-per-page', None)
            if not per_page:
                per_page = 2  # later we will take the default from config

            starting_content = self

            pg_stream = PaginationStream(self.__config, starting_content, rules_txt, per_page)

    @property
    def pagination(self):
        return self.__pagination

    @pagination.setter
    def pagination(self, pg):
        assert self.__pagination is None
        self.__pagination = pg

    def get_content_wrapper(self):
        # TODO: should place in contract!
        # So, with cotract it can be used in paginator too
        return ContentWrapper(self)


class ContentWrapper:

    __slots__ = ('__content', )

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


class TextModule(ContentModuleContract):

    _file_name_regex = re.compile("^(?P<id>[0-9]+)\. ?(.+)")

    def __init__(self, _cfg):
        self.__config = _cfg
        self.__text_map = {}

        self.__is_loaded = False

    @property
    def name(self):
        return normalize_key('text')

    @property
    def config(self):
        return self.__config

    @property
    def content_class(self):
        return TextContent

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
        # url_str = url_str.lstrip('/')  # Don't do this

        if url_str.endswith('/'):
            is_dir = True
        else:
            if '.' in url_str:
                is_dir = False
        # url_str = url_str.rstrip('/')  # Don't do this - commenting for now

        if self.root_url_path:
            url_str += self.root_url_path

        url = ContentUrl(self.__config, url_str, is_dir=is_dir)
        return url

    @not_loaded
    def load(self):
        paths = self.__config.path_tree.get_module_paths(self)
        file_ids = set()

        for file_path in paths:
            if file_path.extension.lower() in self.extensions:
                has_file_id = False
                file_base_match = file_path.match_basename(self.__class__._file_name_regex)

                if file_base_match:
                    # raise Exception("File name %s does not go with the file name format")
                    has_file_id = True

                if file_base_match:
                    text_id = file_base_match.group('id').lstrip('0')
                    if text_id in file_ids:
                        raise Exception("Two different texts files cannot have the same text id")
                else:
                    text_id = None

                # print("::::: %s" % file_path.absolute_path)
                with self.__config.path_tree.open_file(file_path.relative_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    text_obj = TextContent(self.__config, self, file_path, text)
                    text_obj.url_object = self._create_url_object(text_obj.frontmatter)

                    if not text_obj.has_valid_frontmatter:
                        print(text_obj.raw_frontmatter)
                        raise Exception("Front matter is corrupted or invalid")
                    self.__text_map[text_id] = text_obj
                    self.__config.add_document(text_obj)
            else:
                self.__config.enqueue_static_file(self, file_path)

        # TODO: must be moved to config.load later
        for text_obj in self.__text_map.values():
            text_obj.trigger_pagination()

        self.__is_loaded = True

    @property
    def extensions(self):
        return {'md', 'markdown'}

    @property
    def root_url_path(self):
        return ""
