"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


class Pagination:
    def __init__(self, total_pagination, contents, position, per_page):
        assert len(contents) != 0
        self.__total_pagination = total_pagination
        self.__contents = contents
        self.__position = position
        self.__per_page = per_page
        self.__hosting_content = None
        self.__next_page = None
        self.__prev_page = None

    @property
    def total_pagination(self):
        return self.__total_pagination

    @property
    def contents(self):
        return self.__contents

    @property
    def position(self):
        return self.__position

    @property
    def contents_per_page(self):
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


class PaginationStream:
    def __init__(self, config, starting_content, filter_txt, contents_per_page=2):
        self.__config = config
        self.__starting_content = starting_content
        self.__filter_txt = filter_txt
        self.__paginations = None
        self.__contents_per_page = contents_per_page
        self.__aux_contents = self.__paginate()

    def __paginate(self):

        rules_txt = self.__filter_txt
        per_page = self.__contents_per_page
        cnts = self.__config.filter_content(rules_txt)
        print("__paginate():\n\n%s" % str(cnts))
        aux_contents = []

        paginations = []
        paginated_contents = []

        if cnts:
            q, r = divmod(len(cnts), per_page)
            divs = q
            if r > 0:
                divs += 1

            for i in range(divs):
                _cts = []
                for j in range(per_page):
                    idx = (i*per_page) + j           # (row * NUMCOLS) + column        #(i * divs) + j
                    if idx >= len(cnts):
                        break
                    _cts.append(cnts[idx].get_content_wrapper())
                paginated_contents.append(tuple(_cts))

        if paginated_contents:
            i = 0
            prev_page = None
            for _page_contents in paginated_contents:

                pagination = Pagination(len(paginated_contents), _page_contents, i, per_page)
                paginations.append(pagination)

                if i == 0:
                    self.__starting_content.pagination = pagination
                    pagination.host_page = self.__starting_content.get_content_wrapper()
                    prev_page = self.__starting_content

                else:
                    aux = self.__starting_content.create_auxiliary(pagination.position)

                    aux.pagination = pagination
                    pagination.host_page = aux

                    pagination.previous_page = prev_page.get_content_wrapper()
                    # TODO: content wrapper for prev/next page : done but it is still not in contract
                    prev_page.pagination.next_page = aux.get_content_wrapper()
                    prev_page = aux

                    aux_contents.append(aux)
                i += 1

        self.__paginations = tuple(paginations)
        return tuple(aux_contents)

    @property
    def auxiliary_contents(self):
        return self.__aux_contents

    @property
    def paginations(self):
        return self.__paginations

    def __bool__(self):
        return True if len(self.paginations) > 0 else False

    def __len__(self):
        return len(self.paginations)

