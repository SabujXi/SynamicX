from synamic.content_modules.text import TextModule, TextContent
from synamic.core.functions.normalizers import normalize_key, normalize_keys

"""
# Series Specific Frontmatter Example:

Chapters: # case insensitive
    - Chapter: # Starts with 'chapter', anything may follow it.
        for: # may contain a numeric id, relative url_object, full (optionally external) url_object.
        title: # if the value is <get> then it is get from the text if the 'for' key refers to some text
                
    -  Chapter XX: 
         for:
         title: 

for:
----
'for' can contain an id in the form of @text-content-id, or it can have a direct http(s) link.

'title' is optional when there is a content id in 'for'. In this case if the title is omitted then title will be taken 
from the content. Presence of title overrides the title of the content. Title cannot be avoided for absolute links.
"""


class Chapter:
    def __init__(self, serial, title, link):
        self.__serial = serial
        self.__title = title
        self.__link = link

    @property
    def serial(self):
        return self.__serial

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link


class SeriesContent(TextContent):
    def __init__(self, config, module_object, path_object, file_content):
        super().__init__(config, module_object, path_object, file_content)
        self.__chapters = None

    def trigger_pagination(self):
        """
        Do nothing. 
        """

    @property
    def chapters(self):
        if self.__chapters is None:
            _chapters = self.frontmatter.values.get(normalize_key('chapters'), None)
            if _chapters:
                raw_chapters = []
                normalize_keys(_chapters)
                for maybe_chapter in _chapters:
                    for key in maybe_chapter.keys():
                        if key.startswith(normalize_key('chapter')):
                            raw_chapters.append(maybe_chapter[key])

                chapters = []
                for raw_chapter in raw_chapters:
                    cont_ = raw_chapter.get(normalize_key('for'))
                    if cont_.lower().startswith('http://') or cont_.lower().startswith('https://'):
                        url = cont_
                    else:
                        cont_id = cont_.lstrip('@')
                        # self.config.
            else:
                self.__chapters = []

        return self.__chapters


class SeriesModule(TextModule):

    @property
    def name(self):
        return normalize_key('series')

    @property
    def dependencies(self):
        return {normalize_key('text')}

    @property
    def content_class(self):
        return SeriesContent

    @property
    def extensions(self):
        return {'md', 'markdown'}

