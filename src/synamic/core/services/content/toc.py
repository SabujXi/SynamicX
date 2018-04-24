class _Header:
    def __init__(self, level, text, html_id):
        self.__level = int(level)
        self.__text = text
        self.__html_id = html_id
        self.__children = []

    @property
    def level(self):
        return self.__level

    @property
    def text(self):
        return self.__text

    @property
    def html_id(self):
        return self.__html_id

    @property
    def html(self):
        if not self.children:
            res = "<li class='synamic-toc-header-%s-li'><a href='#%s'>%s</a></li>" % (
                self.level, self.html_id, self.text
            )
        else:
            child_strs = []
            for child in self.__children:
                if len(child.children) == 0:
                    child_strs.append(
                        "<li class='synamic-toc-header-%s'><a href='#%s'>%s</a></li>" % (
                            child.level, child.html_id, child.text)
                    )
                else:
                    child_strs.append(
                        "<li class='synamic-toc-header-%s'><a href='#%s'>%s</a><ul>%s</ul></li>" % (
                            child.level, child.html_id, child.text, child.html)
                    )
            child_str = "\n".join(child_strs)
            res = "<li class='synamic-toc-header-%s-li'><a href='#%s'>%s</a><ul>%s</ul></li>" % (
                self.level, self.html_id, self.text, child_str
            )

        return res

    def add(self, header):
        def findnkill(children, header):
            children_reverse = children.copy(); children_reverse.reverse()
            for child in children_reverse:
                if header.level > child.level:
                    child.children.append(header)
                    return
                else:
                    findnkill(child.children, header)
        if self.level + 1 == header.level:
            self.children.append(header)
        else:
            findnkill(self.children, header)

    @property
    def children(self):
        return self.__children

    def __str__(self):
        return self.html

    def __repr__(self):
        return repr(str(self))


class Toc:
    def __init__(self):
        self.__headers = []

    def __bool__(self):
        return bool(self.__headers)

    def add(self, level, text, html_id):
        level = int(level)
        header = _Header(level, text, html_id)
        if len(self.__headers) == 0 or level == 1:
            self.__headers.append(header)
        else:
            last_header = self.__headers[-1]
            if last_header.level > 1 and last_header.level >= header.level:
                self.__headers.append(header)
            else:
                last_header.add(header)

    @property
    def html(self):
        if len(self.__headers) == 0:
            return ""
        return "<ul class='synamic-toc-primary-ul'>%s<ul>" % "\n".join(header.html for header in self.__headers)

    def __str__(self):
        return self.html

    def __repr__(self):
        return str(self)
