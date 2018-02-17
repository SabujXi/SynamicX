class Chapter:
    def __init__(self, config, chapter_field):
        self.__config = config
        self.__chapter_field = chapter_field

        self.__title = chapter_field.get('title').value
        self.__link = None

    @property
    def link(self):
        if self.__link is None:
            l = self.__chapter_field.get('link').value.strip()
            if l.startswith('geturl://'):
                gurl = l[len('geturl://'):]
                link = self.__config.get_url(gurl)
            else:
                link = l
            self.__link = link
        return self.__link

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


def get_chapters(config, chapters_field):
    chapters = []
    chapter_fields = chapters_field.get_multi('chapter')
    for cf in chapter_fields:
        if cf.get('title') is not None and cf.get('link') is not None:
            chapters.append(Chapter(config, cf))
    return tuple(chapters)
