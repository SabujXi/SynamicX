"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
from synamic.core.contracts.content import ContentContract, CDocType


class StaticContent(ContentContract):
    def __init__(self, site, cfields):
        self.__site = site
        self.__cfields = cfields

        # validation
        assert CDocType.is_binary(self.cfields.cdoctype)
        assert cfields.cpath is not None

    @property
    def site(self):
        return self.__site

    def get_stream(self):
        file = self.__cfields.cpath.open('rb')
        return file

    @property
    def body(self):
        # TODO: body should not be allowed for binary files. Fix it later.
        with self.get_stream() as f:
            res = f.read()
        return res

    @property
    def body_as_string(self):
        return self.body.decode('utf-8')

    @property
    def body_as_bytes(self):
        return self.body

    @property
    def cfields(self):
        return self.__cfields

    def __getitem__(self, key):
        return self.__cfields[key]

    def __getattr__(self, key):
        return getattr(self.__cfields, key)
