class Pagination:
    def __init__(self, total_pagination, contents, position, per_page):
        assert len(contents) != 0
        self.__total_pagination = total_pagination
        self.__contents = contents
        self.__position = position
        self.__per_page = per_page
        self.__hosting_content = None

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
    def per_page(self):
        return self.__per_page

    @property
    def hosting_content(self):
        return self.__hosting_content

    @hosting_content.setter
    def hosting_content(self, hos_con):
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
    def has_previous(self):
        if self.__position > 0:
            return True
        return False


class PaginationStream:
    def __init__(self, config, filter_txt, contents_per_page=2):
        self.__config = config
        # self.__starting_content = starting_content
        self.__filter_txt = filter_txt
        self.__paginations = []
        pgs = self._paginate(self.__filter_txt, contents_per_page)
        i = 0

        for pg in pgs:
            self.__paginations.append(Pagination(len(pgs), pg, i, contents_per_page))
            i += 1

    @property
    def paginations(self):
        return self.__paginations

    def _paginate(self, rules_txt, per_page):
        cnts = self.__config.filter_content(rules_txt)

        paginated_contents = []

        if cnts:
            print("Contents: %s" % cnts)
            q, r = divmod(len(cnts), per_page)
            divs = q
            if r > 0:
                divs += 1
            print("Divs: %s" % divs)

            for i in range(divs):
                _cts = []
                for j in range(per_page):
                    idx = (i*per_page) + j           # (row * NUMCOLS) + column        #(i * divs) + j
                    print("idx: %s" % idx)
                    if idx >= len(cnts):
                        break
                    print("IDX %s - %s" % (idx, cnts))
                    _cts.append(cnts[idx])
                paginated_contents.append(tuple(_cts))
        print("Paginated contents: %s" % paginated_contents)
        # if paginated_contents:
        #     i = 1
        #     for page in paginated_contents:
        #         auxiliary_content = content_obj.create_auxiliary(str(i))  # Currently it is creating paginated content
        #         # relative to every cloned
        #         print("Creating auxiliary: %s" % i)
        #         self.add_url(auxiliary_content.url_object)
        #         i += 1
        print("\n~~~~~~~~~~~~~~~~| Paginated contents: %s |~~~~~~~~~~~~~\n" % paginated_contents)
        return paginated_contents


