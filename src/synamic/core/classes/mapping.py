"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


def _callable_when_not_finalized(meth):
    def wrapper(self, *args, **kwargs):
        if self.finalized:
            raise Exception("FinalizableDict cannot be modified once it is finalized")
        return meth(self, *args, **kwargs)
    return wrapper


class FinalizableDict(dict):
    __slots__ = ('__finalized',)

    def __init__(self, *itable, **kwargs):
        super().__init__(*itable, **kwargs)
        self.__finalized = False

    @property
    def finalized(self):
        return self.__finalized

    @_callable_when_not_finalized
    def finalize(self):
        self.__finalized = True

    @_callable_when_not_finalized
    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

    @_callable_when_not_finalized
    def __delitem__(self, key):
        return super().__delitem__(key)

    @_callable_when_not_finalized
    def update(self, m, **kwargs):
        return super().update(m, **kwargs)

    @_callable_when_not_finalized
    def clear(self):
        return super().clear()
