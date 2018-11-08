import io
from synamic.core.contracts import ContentContract, DocumentType


class PaginatedContent(ContentContract):
    def __init__(self, site, origin_cfields, curl, paginated_cfields, document_type):
        self.__site = site
        self.__origin_cfields = origin_cfields
        self.__curl = curl
        self.__cfields = paginated_cfields
        self.__model = paginated_cfields.cmodel
        self.__document_type = document_type
        self.__mime_type = 'text/html'  # TODO: remove hard coding.

        # validation
        assert DocumentType.is_text(self.__document_type)

    @property
    def site(self):
        return self.__site

    @property
    def document_type(self):
        return self.__document_type

    @property
    def cpath(self):
        raise NotImplemented

    @property
    def curl(self):
        return self.__curl

    def get_stream(self):
        template_name = self.__cfields.get('template', 'default.html')
        templates = self.__site.get_service('templates')
        res = templates.render(template_name, context={
            'site': self.__site,
            'content': self
        })
        f = io.BytesIO(res.encode('utf-8'))
        return f

    @property
    def mime_type(self):
        return self.__mime_type

    @property
    def body(self):
        content = self.__site.object_manager.get_marked_content(self.__origin_cfields.cpath)
        assert content is not None
        return content.body

    @property
    def cfields(self):
        return self.__cfields

    @property
    def toc(self):
        raise NotImplemented

    def __get(self, key):
        return self.__cfields.get(key, None)

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return "Paginated content: <%s>\n" % self['title'] + '...'

    def __repr__(self):
        return str(self)


class PaginationPage:
    def __init__(self, site, total_pagination, cfields_s, position, per_page):
        # assert len(cfields_s) != 0
        self.__site = site
        self.__total_pagination = total_pagination
        self.__cfields_s = cfields_s
        self.__position = position
        self.__per_page = per_page

        assert position < total_pagination
        # settable once.
        self.__host_content = None
        self.__next_content = None
        self.__prev_content = None

        # only available to root page/pagination
        self.__sub_pages = None

    @property
    def total_pagination(self):
        return self.__total_pagination

    @property
    def cfields_s(self):
        return self.__cfields_s

    @property
    def contents(self):
        if self.__cfields_s:
            contents = self.__site.object_manager.get_marked_contents_by_cpaths(
                cfields.cpath for cfields in self.__cfields_s
            )
            assert contents
        else:
            contents = tuple()

        return contents

    @property
    def position(self):
        return self.__position

    @property
    def per_page(self):
        return self.__per_page

    @property
    def host_content(self):
        return self.__host_content

    @host_content.setter
    def host_content(self, hos_con):
        assert self.__host_content is None
        self.__host_content = hos_con

    # Synthetic ones

    @property
    def is_start(self):
        if self.__position == 0:
            return True
        return False

    @property
    def is_end(self):
        if self.__position == self.__total_pagination - 1:
            return True
        else:
            return False

    @property
    def is_only(self):
        if self.__total_pagination == 1:
            return True
        return False

    @property
    def has_next(self):
        if self.__position < self.__total_pagination - 1:
            return True
        return False

    @property
    def next_content(self):
        return self.__next_content

    @next_content.setter
    def next_content(self, np):
        assert self.__next_content is None
        self.__next_content = np

    @property
    def has_previous(self):
        if self.__position > 0:
            return True
        return False

    @property
    def previous_content(self):
        return self.__prev_content
    prev_content = previous_content

    @previous_content.setter
    def previous_content(self, pp):
        assert self.__prev_content is None
        self.__prev_content = pp

    @property
    def sub_pages(self):
        assert self.is_start, "Cannot use this method for non root pages"

        sub_pages = self.__sub_pages
        if sub_pages is None:
            assert self.__per_page == 0, "Sub pages was not set after creation or per_page was set to wrong value"
            return tuple()
        else:
            return sub_pages

    @sub_pages.setter
    def sub_pages(self, sub_pages):
        assert self.is_start, "Cannot use this method for non root pages"

        assert self.__sub_pages is None
        assert isinstance(sub_pages, (list, tuple))
        self.__sub_pages = sub_pages

    def get_sub_page(self, idx, default=None):
        assert idx > 0, "Root/start pagination is considered 0 and this method is only available on root"
        sub_pages = self.sub_pages
        if idx >= len(sub_pages):
            return default
        else:
            return sub_pages[idx - 1]

    @property
    def is_empty(self):
        return self.__bool__()

    def __bool__(self):
        return self.__per_page > 0

    def __str__(self):
        return "Pagination Page: %d" % self.__position

    def __repr__(self):
        return repr(self.__str__())

    @classmethod
    def paginate_cfields(cls, site, origin_content, queried_cfields_s, per_page):
        site_settings = site.object_manager.get_site_settings()
        url_partition_comp = site_settings['url_partition_comp']
        pagination_url_comp = site_settings['pagination_url_comp']

        paginated_cfields_s_divisions = []

        if queried_cfields_s:
            quotient, remainder = divmod(len(queried_cfields_s), per_page)
            divisions = quotient
            if remainder > 0:
                divisions += 1

            for division_idx_i in range(divisions):
                division_cfields_s = []
                for idx_in_division_j in range(per_page):
                    idx = (division_idx_i * per_page) + idx_in_division_j  # (row * NUMCOLS) + column        #(i * divisions) + j
                    if idx >= len(queried_cfields_s):
                        break

                    # creating paginated content
                    original_cfields = queried_cfields_s[idx]
                    division_cfields_s.append(original_cfields)
                paginated_cfields_s_divisions.append(tuple(division_cfields_s))

        paginations = []
        paginated_contents = []
        if paginated_cfields_s_divisions:
            prev_page = None
            for division_idx_i, division_cfields_s in enumerate(paginated_cfields_s_divisions):
                pagination = PaginationPage(
                    site,
                    len(paginated_cfields_s_divisions),
                    division_cfields_s,
                    division_idx_i,
                    per_page
                )
                paginations.append(pagination)

                if division_idx_i == 0:
                    # setting pagination to the host content
                    origin_content.cfields.set('pagination', pagination)

                    pagination.host_content = origin_content
                    prev_page = origin_content

                else:
                    # creating paginated content
                    document_type = DocumentType.GENERATED_HTML_DOCUMENT
                    curl = origin_content.curl.join(
                        "/%s/%s/%d/" % (url_partition_comp, pagination_url_comp, division_idx_i + 1),
                        for_document_type=document_type)
                    paginated_cfields = origin_content.cfields.as_generated(
                        curl, document_type=document_type
                    )
                    paginated_cfields.set(
                        'title',
                        origin_content.cfields.get('title') + " - %s %d" % (pagination_url_comp.title(), division_idx_i + 1)
                    )
                    paginated_content = PaginatedContent(
                        site,
                        origin_content.cfields,
                        curl,
                        paginated_cfields,
                        document_type,
                    )

                    # setting pagination to an aux content
                    paginated_content.cfields.set('pagination', pagination)
                    pagination.host_content = paginated_content

                    pagination.previous_content = prev_page
                    # TODO: content wrapper for prev/next page
                    prev_page.pagination.next_content = paginated_content
                    prev_page = paginated_content

                    paginated_contents.append(paginated_content)

        if not paginations:
            pagination = PaginationPage(
                site,
                1,
                tuple(),
                0,
                0
            )
            origin_content.cfields.set('pagination', pagination)
        paginations[0].sub_pages = paginations[1:]
        return tuple(paginations), tuple(paginated_contents)
