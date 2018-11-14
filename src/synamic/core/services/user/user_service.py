"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
from synamic.core.standalones.functions.decorators import not_loaded
from synamic.core.contracts import CDocType


class UserService:
    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False
        self.__menu_dir = self.__site.system_settings['dirs.metas.users']

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # for file_path in file_paths:
        self.__is_loaded = True

    def make_user(self, user_id):
        path_tree = self.__site.get_service('path_tree')
        fn = user_id + '.syd'
        path = path_tree.create_file_cpath(self.__menu_dir, fn)
        syd = self.__site.object_manager.get_syd(path)

        user_obj = self.__User(
            self.__site,
            user_id,
            syd
        )
        return user_obj

    def get_user_ids(self):
        user_ids = []
        path_tree = self.__site.get_service('path_tree')
        users_cdir = path_tree.create_dir_cpath(self.__menu_dir)
        if users_cdir.exists():
            user_cfiles = users_cdir.list_files(depth=1)
            for menu_cfile in user_cfiles:
                basename = menu_cfile.basename
                if basename.lower().endswith('.syd'):
                    menu_name = basename[:-len('.syd')]
                    user_ids.append(menu_name)
        return tuple(user_ids)

    @classmethod
    def is_type_user(cls, other):
        return isinstance(other, cls.__User)

    class __User:
        def __init__(self, site, user_id, user_fields):
            self.__site = site
            self.__user_id = user_id.lower()
            self.__user_fields = user_fields

            # validation
            assert isinstance(self.__user_id, str)

            # calculate name
            name = self.__user_fields.get('name', None)
            if name is None:
                self.__user_fields.set('name', self.__user_id)
            self.__name = name

            # content
            self.__synthetic_cfields = None
            self.__content = None

        @property
        def id(self):
            return self.__user_id

        @property
        def name(self):
            return self.__name

        @property
        def cfields(self):
            if self.__synthetic_cfields is not None:
                sf = self.__synthetic_cfields
            else:
                system_settings = self.__site.system_settings
                content_service = self.__site.get_service('contents')
                url_partition_comp = system_settings['url_partition_comp']
                user_url_comp = system_settings['user_url_comp']
                cdoctype = CDocType.GENERATED_HTML_DOCUMENT
                mimetype = 'text/html'
                curl = self.__site.synamic.router.make_url(
                    self.__site, f'/{url_partition_comp}/{user_url_comp}/{self.id}', for_cdoctype=cdoctype
                )
                sf = content_service.make_synthetic_cfields(
                    curl,
                    cdoctype,
                    mimetype,
                    cpath=None,
                    fields_map=None)
                sf['title'] = self.title if self.title else self.name
                sf['author'] = self
                self.__synthetic_cfields = sf
            return sf

        @property
        def curl(self):
            return self.cfields.curl

        def __user_content_renderer(self, site, gen_content):
            site_settings = site.settings
            template_service = site.get_service('templates')
            user_template_name = site_settings['templates.user']

            html_text_content = template_service.render(
                user_template_name,
                site=site,
                content=gen_content,
                author=self,
            )
            return html_text_content

        @property
        def content(self):
            if self.__content is not None:
                content = self.__content
            else:
                content_service = self.__site.get_service('contents')

                content = content_service.build_generated_content(
                    self.cfields,
                    '',
                    source_cpath=None,
                    render_callable=self.__user_content_renderer)
                self.__content = content
            return content

        @property
        def contents(self):
            return self.__site.object_manager.query_contents(f'author == {self.id} :sortby created_on desc')

        def __getattr__(self, item):
            return self.__user_fields.get(item, None)

        def __getitem__(self, item):
            return self.__user_fields.get(item, None)

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return self.id == other.id

        def __hash__(self):
            return hash(self.id)

        def __str__(self):
            return "User (%s) : %s" % (self.id, self.name)

        def __repr__(self):
            return repr(str(self))

