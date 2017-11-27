def loaded(f):
    def method_wrapper(self, *args, **kwargs):
        assert self.is_loaded, "Must be loaded before this method can be called"
        return f(self, *args, **kwargs)
    return method_wrapper


def not_loaded(f):
    def method_wrapper(self, *args, **kwargs):
        assert not self.is_loaded, "Must NOT be loaded before this method can be called"
        return f(self, *args, **kwargs)
    return method_wrapper
