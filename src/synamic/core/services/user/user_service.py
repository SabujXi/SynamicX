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
from synamic.core.contracts import DocumentType


class UserService:
    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False
        self.__menu_dir = self.__site.default_data.get_syd('dirs').get('metas.users')

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
        menu_cfiles = users_cdir.list_files(depth=1)
        for menu_cfile in menu_cfiles:
            basename = menu_cfile.basename
            if basename.lower().endswith('.syd'):
                menu_name = basename[:-len('.syd')]
                user_ids.append(menu_name)
        return tuple(user_ids)

    class __User:
        def __init__(self, site, user_id, user_fields=None):
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
                site_settings = self.__site.object_manager.get_site_settings()
                content_service = self.__site.get_service('contents')
                url_partition_comp = site_settings['url_partition_comp']
                document_type = DocumentType.GENERATED_HTML_DOCUMENT
                curl = self.__site.synamic.router.make_url(
                    self.__site, '/%s/user/%s' % (url_partition_comp, self.id), for_document_type=document_type
                )
                sf = synthetic_fields = content_service.make_synthetic_content_fields(
                    curl,
                    document_type=document_type,
                    fields_map=None)
                sf['title'] = self.title if self.title else self.name
                sf['author'] = self
                self.__synthetic_cfields = synthetic_fields
            return sf

        @property
        def curl(self):
            return self.cfields.curl

        @property
        def content(self):
            if self.__content is not None:
                content = self.__content
            else:
                site_settings = self.__site.object_manager.get_site_settings()
                template_service = self.__site.get_service('templates')
                content_service = self.__site.get_service('contents')
                user_template_name = site_settings['templates.user']

                content = content_service.build_generated_content(
                    self.cfields,
                    self.cfields.curl,
                    None,
                    document_type=self.cfields.document_type,
                    mime_type='text/html',
                    source_cpath=None)
                html_text_content = template_service.render(user_template_name, site=self.__site, content=content, author=self)
                content.__set_file_content__(html_text_content)
                # TODO: fix this content setting later.
                self.__content = content
            return content

        def contents(self):
            raise NotImplemented

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

