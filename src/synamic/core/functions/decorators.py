"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


def loaded(f):
    def method_wrapper(self, *args, **kwargs):
        assert self.is_loaded, "Class object of the method `%s`'s must be loaded before this method can be called" % f.__qualname__
        return f(self, *args, **kwargs)
    return method_wrapper


def not_loaded(f):
    def method_wrapper(self, *args, **kwargs):
        assert not self.is_loaded, "Must NOT be loaded before this method can be called"
        return f(self, *args, **kwargs)
    return method_wrapper
