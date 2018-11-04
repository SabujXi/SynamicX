"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import io
from synamic.core.contracts.content import ContentContract, DocumentType


class GeneratedContent(ContentContract):
    def __init__(self, site, url_object, content_id, file_content,
                 document_type=DocumentType.GENERATED_TEXT_DOCUMENT, mime_type='octet/stream', source_cpath=None, **kwargs):
        if file_content is None:
            assert source_cpath is not None

        assert site.get_service('contents').is_type_content_id(content_id)
        self.__site = site
        self.__url_object = url_object
        self.__content_id = content_id
        self.__file_content = file_content
        self.__document_type = document_type
        self.__mime_type = mime_type
        self.__source_cpath = source_cpath

        # kwargs for use in special subclasses where private variables are not accessible.
        self.__kwargs = kwargs.copy()

        # validation
        assert DocumentType.is_generated(self.__document_type)
        assert type(self.__file_content) in (type(None), bytes, bytearray)
        assert bool(content_id) or content_id == 0

    @property
    def id(self):
        return self.__content_id

    @property
    def site(self):
        return self.__site

    @property
    def path_object(self):
        raise Exception("Generated content cannot have cpath object")

    @property
    def url_object(self):
        return self.__url_object

    def get_stream(self):
        if self.__file_content is not None:
            if isinstance(self.__file_content, (bytes, bytearray)):
                file = io.BytesIO(self.__file_content)
            else:
                assert isinstance(self.__file_content, str)
                file = io.BytesIO(self.__file_content.encode('utf-8'))
        else:
            file = self.__source_cpath.open('rb')
        return file

    @property
    def mime_type(self):
        return self.__mime_type

    @property
    def document_type(self):
        return self.__document_type

    # non content contract attrs
    @property
    def kwargs(self):
        return self.__kwargs

    @property
    def source_cpath(self):
        return self.__source_cpath

    @property
    def file_content(self):
        if self.__file_content is not None:
            return self.__file_content
        else:
            with self.get_stream() as stream:
                content = stream.read()
                return content
