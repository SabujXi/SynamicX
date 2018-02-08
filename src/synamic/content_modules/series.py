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
    def __init__(self, serial, title, link, module_name=None, content_id=None):
        self.__serial = serial
        self.__title = title
        self.__link = link
        self.__module_name = module_name
        self.__content_id = content_id

    @property
    def serial(self):
        return self.__serial

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link

    @property
    def module_name(self):
        return self.__module_name

    @property
    def content_id(self):
        return self.__content_id


class SeriesContent(MarkedContentImplementation):
    def __init__(self, config, module_object, path_object, file_content):
        super().__init__(config, module_object, path_object, file_content)
        self.__chapters = None
        # print("\n\nCreating series content objectn\n\n")
        # module_object.index_mod_n_cid(self.frontmatter.values.get(normalize_key('chapters'), None), self)

    def trigger_pagination(self):
        """
        Do nothing. 
        """
        return tuple()

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
                serial = 1
                for raw_chapter in raw_chapters:
                    for_ = raw_chapter.get(normalize_key('for'))
                    title = raw_chapter.get(normalize_key('title'), None)
                    if for_.lower().startswith('http://') or for_.lower().startswith('https://'):
                        url = for_
                        mod_name = None
                        cont_id = None
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
                        cont = self.config.get_document_by_id(mod_name, cont_id)
                        # TODO: devise the following thing to absolute path.
                        url = cont.url_object.path
                        title = cont.title
                    if title is None:
                        title = url
                    chapters.append(Chapter(serial, title, url, mod_name, cont_id))
                    serial += 1
                self.__chapters = chapters
            else:
                self.__chapters = []
        return self.__chapters


class SeriesModule(MarkedContentModuleImplementation):
    def __init__(self, *args):
        super().__init__(*args)
        self.__mod_name__content_id = {}

    @property
    def name(self):
        return 'series'

    @property
    def dependencies(self):
        return {'text'}

    @property
    def content_class(self):
        return SeriesContent

    def load(self):
        super().load()
        for dynamic_content in self.dynamic_contents:
            cont_id = dynamic_content.content_id
            if cont_id is not None:
                pass

    def index_mod_n_cid(self, _chapters, series_content):
        # index module and content id
        if _chapters:
            _chapters = _chapters.copy()
            raw_chapters = []
            normalize_keys(_chapters)
            for maybe_chapter in _chapters:
                for key in maybe_chapter.keys():
                    if key.startswith(normalize_key('chapter')):
                        raw_chapters.append(maybe_chapter[key])
            for raw_chapter in raw_chapters:
                for_ = raw_chapter.get(normalize_key('for'))
                if not (for_.lower().startswith('http://') or for_.lower().startswith('https://')):
                    for_ = for_.lstrip('@')
                    mod_n_id = for_.split(':')
                    if len(mod_n_id) == 2:
                        mod_name = mod_n_id[0]
                        cont_id = mod_n_id[1]
                    else:
                        assert len(mod_n_id) == 1
                        mod_name = 'text'
                        cont_id = mod_n_id[0]

                    # index
                    if mod_name not in self.__mod_name__content_id:
                        mod_name_d = self.__mod_name__content_id[mod_name] = {}
                    else:
                        mod_name_d = self.__mod_name__content_id[mod_name]

                    if cont_id not in mod_name_d:
                        cont_id_set = mod_name_d[cont_id] = set()
                    else:
                        cont_id_set = mod_name_d[cont_id]
                    cont_id_set.add(series_content)

    def get_all_series_by_mod_name_n_cid(self, mod_name, cid):
        if mod_name not in self.__mod_name__content_id:
            return None
        else:
            if cid not in self.__mod_name__content_id[mod_name]:
                return None
            else:
                return self.__mod_name__content_id[mod_name][cid]
