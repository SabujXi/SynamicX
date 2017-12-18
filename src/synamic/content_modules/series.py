from synamic.content_modules.reference_implementations import MarkedContentModuleImplementation, MarkedContentImplementation
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


class SeriesContent(MarkedContentImplementation):
    def __init__(self, config, module_object, path_object, file_content):
        super().__init__(config, module_object, path_object, file_content)
        self.__chapters = None
        # print("\n\nCreating series content objectn\n\n")

    def trigger_pagination(self):
        """
        Do nothing. 
        """
        return tuple()

    @property
    def chapters(self):
        # input("Give me chapter name")
        if self.__chapters is None:
            _chapters = self.frontmatter.values.get(normalize_key('chapters'), None)
            # print("\n\nChapters:\n")
            # print(_chapters)
            # print("\n\n\n")
            if _chapters:
                raw_chapters = []
                normalize_keys(_chapters)
                for maybe_chapter in _chapters:
                    for key in maybe_chapter.keys():
                        if key.startswith(normalize_key('chapter')):
                            raw_chapters.append(maybe_chapter[key])

                chapters = []
                serial = 1
                for raw_chapter in raw_chapters:
                    for_ = raw_chapter.get(normalize_key('for'))
                    title = raw_chapter.get(normalize_key('title'), None)
                    if for_.lower().startswith('http://') or for_.lower().startswith('https://'):
                        url = for_
                    else:
                        for_ = for_.lstrip('@')
                        mod_n_id = for_.split(':')
                        if len(mod_n_id) == 2:
                            mod_name = mod_n_id[0]
                            cont_id = mod_n_id[1]
                        else:
                            assert len(mod_n_id) == 1
                            mod_name = 'text'
                            cont_id = mod_n_id[0]
                        # TODO: series is hard coded for text at this moment. Change it to fit for other content modules
                        cont = self.config.get_document_by_id(mod_name, cont_id)
                        # TODO: devise the following thing to absolute path.
                        url = cont.url_object.path
                        title = cont.title
                    if title is None:
                        title = url
                    chapters.append(Chapter(serial, title, url))
                    serial += 1
                self.__chapters = chapters
            else:
                self.__chapters = []

        return self.__chapters


class SeriesModule(MarkedContentModuleImplementation):

    @property
    def name(self):
        return 'series'

    @property
    def dependencies(self):
        return {'text'}

    @property
    def content_class(self):
        return SeriesContent
