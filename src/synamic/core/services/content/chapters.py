class Chapter:
    def __init__(self, site, chapter_field):
        self.__site = site
        self.__chapter_field = chapter_field

        self.__title = chapter_field['title']
        del chapter_field['title']
        self.__raw_link = chapter_field['link']
        del chapter_field['link']
        self.__cached_link = None

    @property
    def link(self):
        if self.__cached_link is None:
            self.__cached_link = self.__site.object_manager.getc(self.__raw_link)
        return self.__cached_link

    @property
    def title(self):
        return self.__title

    def __get(self, key):
        self.__chapter_field.get(key, None)

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def to_dict(self):
        d = {
            'link': self.link,
            'title': self.title,
        }
        return d

    def __str__(self):
        return self.to_dict()

    def __repr__(self):
        return repr(self.__str__())

