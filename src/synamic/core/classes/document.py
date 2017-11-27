import re
from synamic.core.functions.frontmatter import parse_front_matter
from synamic.core.functions.yaml_processor import load_yaml
from synamic.core.classes.frontmatter import Frontmatter
from synamic.core.classes.url import ContentUrl
from synamic.core.functions.date_time import parse_datetime


_invalid_url = re.compile(r'^[a-zA-Z0-9]://', re.IGNORECASE)


class MarkedDocument(object):
    def __init__(self, string, config, content):
        self.__string = string
        self.__config = config
        self.__content = content

        self.__front_text = ""
        self.__body_text = ""
        self.__frontmatter = None
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

        # doc properties
        self.__title = None
        self.__url = None
        self.__created_on = None
        self.__updated_on = None
        self.__summary = None
        self.__tags = None
        self.__categories = None

    def __getitem__(self, item):
        return self.frontmatter[item]

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
            self.__frontmatter = Frontmatter(load_yaml(self.raw_frontmatter))
        return self.__frontmatter

    @property
    def body(self):
        return self.__body_text

    @property
    def title(self):
        if self.__title is None:
            ttl = self.frontmatter.get("title")
            if ttl is None:
                self.__title = ""
            else:
                self.__title = ttl
        return self.__title

    @property
    def url(self):
        if self.__url is None:
            url_str = ''
            url_name = None
            is_dir = True
            yaml_url_obj = self.frontmatter['url']

            if isinstance(yaml_url_obj, str):
                url_str = yaml_url_obj
            else:
                assert isinstance(yaml_url_obj, dict), "url_representing_obj must be dict object at this phase"
                url_str = yaml_url_obj['url']
                url_name = yaml_url_obj['name']
            assert not _invalid_url.match(url_str), "url cannot have scheme"
            # url_str = url_str.lstrip('/')  # Don't do this

            if url_str.endswith('/'):
                is_dir = True
            else:
                if url_str.lower().endswith(".html") or url_str.lower().endswith(".htm"):
                    is_dir = False
            # url_str = url_str.rstrip('/')  # Don't do this - commenting for now

            if self.__content.module.root_url_path:
                url_str += self.__content.module.root_url_path

            url = ContentUrl(self.__config, self.__content, url_str, url_name, is_dir)
            self.__url = url

        return self.__url

    @property
    def full_url(self):
        return self.url.full_url

    @property
    def created_on(self):
        if self.frontmatter.get('created-on'):
            if self.__created_on is None:
                self.__created_on = parse_datetime(
                    self.frontmatter['created-on']
                )
        else:
            return None
        return self.__created_on

    @property
    def updated_on(self):
        if self.frontmatter.get('updated-on'):
            if self.__updated_on is None:
                self.__updated_on = parse_datetime(
                    self.frontmatter['updated-on']
                )
        else:
            return None
        return self.__updated_on

    @property
    def summary(self):
        if self.__summary is None:
            self.__summary = self.frontmatter.get('summary', "")
        return self.__summary

    @property
    def tags(self):
        if self.__tags is None:
            tgs = self.frontmatter.get('tags', '')
            if tgs:
                self.__tags = [x.strip() for x in tgs.split(',')]
            else:
                self.__tags = []
        return self.__tags

    @property
    def categories(self):
        if self.__categories is None:
            ctgs = self.frontmatter.get('categories', '')
            if ctgs:
                self.__categories = [x.strip() for x in ctgs.split()]
            else:
                self.__categories = []

        return self.__categories

    @property
    def template(self):
        tmplt = self.frontmatter.get('template')
        print("tmplt: ", tmplt)
        print("FM Keys: ", self.frontmatter.keys())
        assert tmplt, "Template must exist"
        l = tmplt.split(":")
        if len(l) > 1:
            template_module_name = l[0]
            template_name = l[1]
        else:
            template_module_name = 'synamic-template'
            template_name = l[0]
        template_mod = self.__config.get_module(template_module_name)
        res = (template_mod, template_name)
        return res
        # template_mod = self.__config.get_module(template_module_name)
        # res = template_mod.render(template_name, body=self.body)
        # return res
