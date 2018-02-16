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
