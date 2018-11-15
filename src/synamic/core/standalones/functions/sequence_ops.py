def is_sequence(target):
    return isinstance(target, (tuple, list))


def are_sequences(*args):
    assert len(args) > 0
    res = True
    for e in args:
        if not is_sequence(e):
            res = False
            break
    return res


class Sequence:
    @staticmethod
    def equals(target, what):
        assert are_sequences(target, what)
        if len(what) != len(target):
            return False
        else:
            equal = True
            for idx, e_target in enumerate(target):
                e_what = what[idx]
                if e_target != e_what:
                    equal = False
                    break
            return equal

    @staticmethod
    def startswith(target, what):
        assert are_sequences(target, what)
        if len(what) == 0 or len(target) == 0:
            return False
        elif len(what) > len(target):
            return False
        else:
            return Sequence.equals(target[:len(what)], what)

    @staticmethod
    def endswith(target, what):
        assert are_sequences(target, what)
        if len(what) == 0 or len(target) == 0:
            return False
        elif len(what) > len(target):
            return False
        else:
            return Sequence.equals(target[len(target) - len(what):], what)

    @staticmethod
    def lstrip(target, what):
        """Unlike string, just strips the first part"""
        assert are_sequences(target, what)
        res = target
        if Sequence.startswith(target, what):
            res = res[len(what):]
        return type(target)(res)

    @staticmethod
    def rstrip(target, what):
        """Unlike string, just strips the last part"""
        assert are_sequences(target, what)
        res = target
        if Sequence.endswith(target, what):
            res = res[:-len(what)]
        return type(target)(res)

    @staticmethod
    def strip(target, what):
        """Unlike string, just strips the first n last part"""
        assert are_sequences(target, what)
        res = target
        if Sequence.endswith(target, what):
            res = res[:-len(what)]
        if Sequence.startswith(target, what):
            res = res[len(what):]
        return type(target)(res)



if __name__ == '__main__':
    # TEST
    assert Sequence.equals([1, 2], list((1, 2)))
    assert Sequence.equals([1, 2], (1, 2))
    assert Sequence.equals([1, 2], [1, 2])
    assert Sequence.startswith((1, 2), [1, ])
    assert Sequence.endswith((1, 2), (2, ))
    assert Sequence.rstrip([1, 2, 3], [2, 3]) == [1], f'{Sequence.rstrip([1, 2, 3], [2, 3])}'
    assert Sequence.lstrip([1, 2, 3], [1, 2, 3]) == []
    assert Sequence.lstrip([1, 2, 3], [2, 2, 3]) == [1, 2, 3]
    assert Sequence.rstrip([1, 2, 3], [2, 2, 3]) == [1, 2, 3]
    print(f'Test positive!')
