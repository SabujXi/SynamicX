__all__ = ['Nil']


class _Nil:
    __instance_count = 0

    def __init__(self):
        assert self.__instance_count == 0, f'Only one instance of Nil can exist in the whole system. Do not try to ' \
                                           f'instantiate by yourself. Use the one synamic.Nil'

        self.__instance_count += 1

    def __eq__(self, other):
        return id(other) == id(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __ge__(self, other):
        return self.__eq__(other)

    def __le__(self, other):
        return self.__eq__(other)

    def __contains__(self, item):
        return False

    def __hash__(self):
        return id(self)

    def __bool__(self):
        return False

    def __str__(self):
        return ''

    def __repr__(self):
        return ''

    def __getattr__(self, item):
        return self


Nil = _Nil()
