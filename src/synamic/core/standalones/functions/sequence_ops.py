def _assert_type(target, what):
    assert type(target) in (tuple, list)
    assert type(what) in (tuple, list)
    return tuple(target), tuple(what)


class Sequence:
    @staticmethod
    def startswith(target, what):
        target, what = _assert_type(target, what)
        if len(what) == 0 or len(target) == 0:
            return False
        elif len(what) > len(target):
            return False
        is_true = True
        idx = 0
        while idx < len(what):
            e_target = target[idx]
            e_what = what[idx]
            idx += 1
            if e_target != e_what:
                is_true = False
                break
        return is_true

    @staticmethod
    def lstrip(target, what):
        target, what = _assert_type(target, what)
        if Sequence.startswith(target, what):
            res = target[len(what):]
        else:
            res = target
        return res

    @staticmethod
    def _contains_w_idx(target, what):
        target, what = _assert_type(target, what)
        if len(what) == 0 or len(target) == 0:
            return False, -1

        idx = 0

        while len(target) > 0:
            if what[0] in target:
                i = target.index(what[0])
                idx += i
                target = target[i:]
                if Sequence.startswith(target, what):
                    return True, idx
            else:
                return False, -1

    @staticmethod
    def contains(target, what):
        return Sequence._contains_w_idx(target, what)[0]

    @staticmethod
    def extract_4m_startswith(target, what):
        target, what = _assert_type(target, what)
        print("extract_4m_startswith: %s, %s (target, what)" % (target, what))
        found, idx = Sequence._contains_w_idx(target, what)
        if found:
            return target[idx+len(what):]
        else:
            return None

