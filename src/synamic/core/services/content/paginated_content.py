import io
from synamic.core.contracts import ContentContract, DocumentType


class PaginatedContent(ContentContract):
    def __init__(self, site, origin_content_fields, url_object, paginated_content_fields, document_type):
        self.__site = site
        self.__origin_content_fields = origin_content_fields
        self.__url_object = url_object
        self.__content_fields = paginated_content_fields
        self.__model = paginated_content_fields.model_object
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
    def path_object(self):
        raise NotImplemented

    @property
    def url_object(self):
        return self.__url_object

    def get_stream(self):
        template_name = self.__content_fields.get('template', 'default.html')
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
        content = self.__site.object_manager.get_marked_content(self.__origin_content_fields.cpath_object)
        assert content is not None
        return content.body

    @property
    def fields(self):
        return self.__content_fields

    @property
    def toc(self):
        raise NotImplemented

    def __get(self, key):
        return self.__content_fields.get(key, None)

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return "Paginated content: <%s>\n" % self['title'] + '...'

    def __repr__(self):
        return str(self)


class PaginationPage:
    def __init__(self, site, total_pagination, contents_fields, position, per_page):
        assert len(contents_fields) != 0
        self.__site = site
        self.__total_pagination = total_pagination
        self.__contents_fields = contents_fields
        self.__position = position
        self.__per_page = per_page
        self.__hosting_content = None
        self.__next_page = None
        self.__prev_page = None

    @property
    def total_pagination(self):
        return self.__total_pagination

    @property
    def contents_fields(self):
        return self.__contents_fields

    @property
    def contents(self):
        if self.__contents_fields:
            contents = self.__site.object_manager.get_marked_contents_by_cpaths(
                content_fields.cpath_object for content_fields in self.__contents_fields
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
    def host_page(self):
        return self.__hosting_content

    @host_page.setter
    def host_page(self, hos_con):
        assert self.__hosting_content is None
        self.__hosting_content = hos_con

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
    def next_page(self):
        return self.__next_page

    @next_page.setter
    def next_page(self, np):
        assert self.__next_page is None
        self.__next_page = np

    @property
    def has_previous(self):
        if self.__position > 0:
            return True
        return False

    @property
    def previous_page(self):
        return self.__prev_page

    @previous_page.setter
    def previous_page(self, pp):
        assert self.__prev_page is None
        self.__prev_page = pp

    def __str__(self):
        return "Pagination Page: %d" % self.__position

    def __repr__(self):
        return repr(self.__str__())

    @classmethod
    def paginate_content_fields(cls, site, origin_content, queried_contents_fieldS, per_page):
        url_partition_comp = site.object_manager.get_site_settings()['url_partition_comp']

        paginated_contents_fieldS_divisions = []

        if queried_contents_fieldS:
            quotient, remainder = divmod(len(queried_contents_fieldS), per_page)
            divisions = quotient
            if remainder > 0:
                divisions += 1

            for division_idx_i in range(divisions):
                division_contents_fieldS = []
                for idx_in_division_j in range(per_page):
                    idx = (division_idx_i * per_page) + idx_in_division_j  # (row * NUMCOLS) + column        #(i * divisions) + j
                    if idx >= len(queried_contents_fieldS):
                        break

                    # creating paginated content
                    original_content_fields = queried_contents_fieldS[idx]
                    division_contents_fieldS.append(original_content_fields)
                paginated_contents_fieldS_divisions.append(tuple(division_contents_fieldS))

        paginations = []
        paginated_contents = []
        if paginated_contents_fieldS_divisions:
            prev_page = None
            for division_idx_i, division_contents_fieldS in enumerate(paginated_contents_fieldS_divisions):
                pagination = PaginationPage(
                    site,
                    len(paginated_contents_fieldS_divisions),
                    division_contents_fieldS,
                    division_idx_i,
                    per_page
                )
                paginations.append(pagination)

                if division_idx_i == 0:
                    # setting pagination to the host content
                    origin_content.fields.set('pagination', pagination)

                    pagination.host_page = origin_content
                    prev_page = origin_content

                else:
                    # creating paginated content
                    document_type = DocumentType.GENERATED_HTML_DOCUMENT
                    url_object = origin_content.url_object.join(
                        "/%s/%d/" % (url_partition_comp, division_idx_i),
                        for_document_type=document_type)
                    paginated_content_fields = origin_content.fields.as_generated(
                        url_object, document_type=document_type
                    )
                    paginated_content_fields.set(
                        'title',
                        origin_content.fields.get('title') + " - %s %d" % ('page', division_idx_i)
                    )
                    paginated_content = PaginatedContent(
                        site,
                        origin_content.fields,
                        url_object,
                        paginated_content_fields,
                        document_type,
                    )

                    # setting pagination to an aux content
                    paginated_content.fields.set('pagination', pagination)
                    pagination.host_page = paginated_content

                    pagination.previous_page = prev_page
                    # TODO: content wrapper for prev/next page : done but it is still not in contract
                    prev_page.pagination.next_page = paginated_content
                    prev_page = paginated_content

                    paginated_contents.append(paginated_content)
        return tuple(paginations), tuple(paginated_contents)
