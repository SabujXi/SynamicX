"""
Limited markdown parser only to parse chapters, nothing more nothing less.
"""
import re
from synamic.exceptions import (
    SynamicError,
    SynamicErrors,
    SynamicPathDoesNotExistError,
    get_source_snippet_from_text
)

__all__ = ['MarkedChapterParser']


# errors
class MismatchedListType(SynamicError):
    pass


class InvalidIndentation(SynamicError):
    pass


class TabsNotAllowed(SynamicError):
    pass


class InvalidLevel(SynamicError):
    pass


class InvalidLine(SynamicError):
    pass


class _Patterns:
    # list item
    list_item = re.compile(r'^(?P<white_spaces>\s*)(?P<item_marker>[*+-]|[0-9]+\. )[ \t]*(?P<item_data>.+)')

    # link pattern
    link = re.compile(
        r"""
        ^[ ]*
        \[
            (?P<link_text>[^\[\]\(]+)
        \]
        \(  
            (
                (?P<link_src>[^()'"]+?)
                ([ \t]+   ('|")   (?P<link_title>.+)   \1)?
            )
        \)
        [ ]*$
        """, re.VERBOSE)

    # blanks
    blanks = re.compile(r'^[ \t]*$')

    # part
    part_header = re.compile(r'^#(?P<text>[^#].*)')


class MarkedChapterParser:
    def __init__(self, site, book_cpath, toc_cpath):
        with toc_cpath.open('r', encoding='utf-8') as fr:
            toc_text = fr.read()

        self.__text = toc_text
        self._chapter_toc = ChaptersTOC(site, book_cpath, toc_cpath)

        self.__item_list_stack = []
        self.__current_blank_lines = 0

    def on_list_item(self, idx, white_spaces, item_marker, item_data):
        # calculate white space
        level = len(white_spaces) // 4
        # print(f'Level: {level}: @.{idx} {item_data} -> {type(item_data)}')

        # determine type of list: when needed
        if item_marker in ('*', '-', '+'):
            # TODO: check marker be equal ... if not start another list closing the last one.
            # check indent too.
            is_ordered = False
        else:
            is_ordered = True

        # CALCULATE PARENT & stack ops #
        # if there were blank lines preceding
        if self.__current_blank_lines:
            self.__current_blank_lines = 0
            # go to the beginning no matter how deep it is nested.
            self.__pop_until_level(0)
            ch_list = ChapterList(self._chapter_toc, parent=None, ordered=is_ordered)
            self.__item_list_stack.append(ch_list)
            parent_list = ch_list
        # ok add the item/list to existing item/list. OR create new one and add
        else:
            # create the very first list & add item to it.
            if len(self.__item_list_stack) == 0:
                if level != 0:
                    raise InvalidLevel(
                        f'Level of the current item is invalid.\n' +
                        f'Source:\n' +
                        get_source_snippet_from_text(text, idx + 1)
                    )

                ch_list = ChapterList(self._chapter_toc, parent=None, ordered=is_ordered)
                self.__item_list_stack.append(ch_list)
                parent_list = ch_list
            # we will use existing list.
            else:
                # assert level > 0, f'Level: {level}'
                # go up one level (if needed) & find the parent matching level if current level is nested
                # one level deeper
                li_parent = self.__item_list_stack[-1]
                # find the real parent list and add item.
                if level == li_parent.level:
                    # self.__pop_until_level(level)
                    parent_list = self.__item_list_stack[-1]
                # this item is indented one level
                elif level - 1 == li_parent.level:
                    list_item = self.__item_list_stack[-1].get_last_item()
                    parent_list = ChapterList(
                        self._chapter_toc,
                        parent=list_item,
                        ordered=is_ordered
                    )
                    list_item.set_list(parent_list)
                    self.__item_list_stack.append(parent_list)
                # this item is dedented any level
                elif level < li_parent.level:
                    self.__pop_until_level(level)
                    parent_list = self.__item_list_stack[-1]

                else:
                    raise InvalidIndentation(
                        'Invalid indentation:: ' + f'Level: {level}, Parent Level: {li_parent.level}\n' +
                        f'Source:\n' +
                        get_source_snippet_from_text(text, idx + 1)
                    )

        # type of current item & li parent must be the same
        if parent_list.is_ordered != is_ordered:
            raise MismatchedListType(
                'Ordered & Unordered list item mixed. Previous'
                ' and current ordering does not match.\n' +
                f'Source:\n' +
                get_source_snippet_from_text(text, idx + 1)
            )

        # OK, now, set the item
        list_item = ListItem(self._chapter_toc, parent_list, item_data)
        if isinstance(item_data, ChLink):
            try:
                ch_link = item_data
                chapter = self._chapter_toc.add_chapter(ch_link)
                # set real url to the ch_link
                ch_link.__set_url__(chapter.url)
            except SynamicError as e:
                raise SynamicErrors(
                    'Error during adding url to chapter toc\n' +
                    f'Source:\n' +
                    get_source_snippet_from_text(self.__text, idx + 1)
                    ,
                    e
                )
        parent_list.add_child(list_item)

    def on_blank_line(self, idx):
        self.__pop_until_level(0)

        self.__current_blank_lines += 1
        # print(f'@.{idx} ... blank ...')

    def on_part(self, idx, part_text):
        self.__pop_until_level(0)

        last_part = self._chapter_toc.get_last_part()
        if last_part is None:
            empty_part_text = ''
            last_part = ChapterPart(empty_part_text)
            self._chapter_toc.add_part(
                last_part
            )
        for ch_list in self.__item_list_stack:
            last_part.add_chapter_list(ch_list)

        # current part
        current_part = ChapterPart(part_text)
        self._chapter_toc.add_part(current_part)

        self.__item_list_stack.clear()

        # print(f'@.{idx} part: {part_text}')

    def on_end(self):
        self.__pop_until_level(0)

        last_part = self._chapter_toc.get_last_part()
        if last_part is None:
            empty_part_text = ''
            last_part = ChapterPart(empty_part_text)
            self._chapter_toc.add_part(
                last_part
            )
            self._chapter_toc.__on_mutation_done__()
        for ch_list in self.__item_list_stack:
            last_part.add_chapter_list(ch_list)
        self.__item_list_stack.clear()

    def on_other(self, idx, text):
        raise InvalidLine(
            'Invalid data that matched no pattern.\n'
            f'Source:\n' +
            get_source_snippet_from_text(self.__text, idx + 1)
        )

    def __pop_until_level(self, level=0):
        while len(self.__item_list_stack) and \
                self.__item_list_stack[-1].level > level:
            self.__item_list_stack.pop()

    def parse(self):
        return self.__lex(self.__text, self)

    def __lex(self, text: str, parser):
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            blank_line_match = _Patterns.blanks.match(line)
            list_item_match = _Patterns.list_item.match(line)
            part_header_match = _Patterns.part_header.match(line)

            # skip blank lines
            if blank_line_match:
                parser.on_blank_line(idx)
                continue
            if list_item_match:
                # when it is a list item
                white_spaces = list_item_match.group('white_spaces')
                item_marker = list_item_match.group('item_marker')
                item_data = list_item_match.group('item_data')

                # tab validation
                if '\t' in white_spaces:
                    raise TabsNotAllowed(
                        'Tabs not allowed for nesting list items.\n' +
                        'Source:\n' +
                        get_source_snippet_from_text(text, idx + 1)
                    )

                # indentation validation
                if len(white_spaces) % 4 != 0:
                    raise InvalidIndentation(
                        f'Indentation must be multiple of zero or more 4 space characters\n' +
                        'Source:\n' +
                        get_source_snippet_from_text(text, idx + 1)
                    )

                # when this list item contains link pattern.
                link_match = _Patterns.link.match(item_data)
                if link_match:
                    link_text = link_match.group('link_text')
                    link_src = link_match.group('link_src')
                    link_title = link_match.group('link_title')
                    item_data = ChLink(self._chapter_toc, link_text, link_src, link_title)
                parser.on_list_item(idx, white_spaces, item_marker, item_data)

            elif part_header_match:
                part_text = part_header_match.group('text')
                parser.on_part(idx, part_text)
            else:
                parser.on_other(idx, line)
        parser.on_end()
        toc = self._chapter_toc
        # self.__init__(toc.site, toc_cpath, self.__text)
        return toc


class ChapterList:
    def __init__(self, chapter_toc, parent=None, ordered=True):
        assert isinstance(chapter_toc, ChaptersTOC)
        assert isinstance(parent, (type(None), ListItem))
        assert parent is not self
        self._chapter_toc = chapter_toc
        self._parent = parent
        self._ordered = ordered
        self._items = []

    @property
    def chapter_toc(self):
        return self._chapter_toc

    @property
    def is_ordered(self):
        return self._ordered

    @property
    def is_unordered(self):
        return not self._ordered

    @property
    def has_parent(self):
        return self._parent is not None

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return tuple(self._items)

    @property
    def has_children(self):
        return len(self._items) > 0

    def add_child(self, item):
        assert isinstance(item, ListItem)
        assert item.parent is self
        self._items.append(item)

    def get_last_item(self):
        return self._items[-1]

    @property
    def is_list(self):
        return True

    @property
    def level(self):
        _max = 10
        level = 0
        parent = self.parent
        while parent is not None:
            parent = parent.parent
            if not isinstance(parent, (ListItem, type(None))):  # not checking None was the bug.
                level += 1
            assert level < _max, 'Ridiculous nesting or bug'
        return level

    def as_html(self, added_level=None):
        descendants = self.children
        res = []
        level = self.level if added_level is None else self.level + added_level
        # if isinstance(self.parent, ListItem):
        #     level += 1
        for child in descendants:
            res.append(child.as_html(added_level=1 + added_level if added_level is not None else 1))

        if self.is_ordered:
            return \
                (level * '    ') + '<ol class="book-toc-chapter-list">\n' + \
                '\n'.join(res) + '\n' +\
                (level * '    ') + '</ol>'
        else:
            return \
                (level * '    ') + '<ul class="book-toc-chapter-list">\n' + \
                '\n'.join(res) + '\n' +\
                (level * '    ') + '</ul>'

    def __str__(self):
        descendants = self.children
        res = []
        level = self.level
        for child in descendants:
            res.append(level * '    ' + str(child))
        return '\n'.join(res)

    def __repr__(self):
        return repr(self.__str__())


class ListItem:
    def __init__(self, chapter_toc, parent, data):
        assert isinstance(chapter_toc, ChaptersTOC)
        assert isinstance(parent, ChapterList)
        assert isinstance(data, (str, ChLink)), f'Type: {type(data)}'
        self._chapter_toc = chapter_toc
        self.__parent = parent
        self.__data = data

        self.__child_list = None

    @property
    def chapter_toc(self):
        return self._chapter_toc

    @property
    def level(self):
        return self.parent.level

    @property
    def data(self):
        return self.__data

    @property
    def has_parent(self):
        return self.__parent is not None

    @property
    def parent(self):
        return self.__parent

    @property
    def is_item(self):
        return True

    @property
    def has_list(self):
        return self.__child_list is not None

    @property
    def child_list(self):
        return self.__child_list

    def set_list(self, l):
        assert self.__child_list is None
        assert isinstance(l, ChapterList)
        assert l.parent is self
        self.__child_list = l

    def as_html(self, added_level=None):
        item_data = f'{self.__data}' if isinstance(self.__data, str) else self.__data.as_html()
        # item_data = '   ' * self.level + item_data
        level = self.level if added_level is None else self.level + added_level
        if not self.__child_list:
            return \
                ('    ' * level) + '<li>' + item_data + '</li>'
        else:
            return \
                '    ' * level + '<li>' + item_data + '\n' + \
                self.__child_list.as_html(added_level=added_level) + '\n' + \
                '    ' * level + '</li>'

    def __str__(self):
        res = []
        res.append(str(self.__data))
        if self.__child_list:
            res.append(str(self.__child_list))
        return '\n'.join(res)

    def __repr__(self):
        return repr(self.__str__())


class ChLink:
    def __init__(self, chapter_toc, link_text, link_src, link_title):
        assert isinstance(chapter_toc, ChaptersTOC)
        self._chapter_toc = chapter_toc
        self.__link_text = link_text
        self.__link_src = link_src
        self.__link_title = link_title
        self.__url = None

    def __set_url__(self, url):
        assert self.__url is None
        self.__url = url

    @property
    def link_text(self):
        return self.__link_text

    @property
    def link_src(self):
        return self.__url if self.__url is not None else self.__link_src

    @property
    def link_title(self):
        return self.__link_title

    def as_html(self):
        title_text = '' if not self.link_title else f' title="{self.link_title}"'
        return f'<a href="{self.link_src}"{title_text}>{self.link_text}</a>'

    def __str__(self):
        return f'{self.link_text}: {self.link_src}, {self.link_title}'

    def __repr__(self):
        return repr(self.__str__())


class Chapter:
    def __init__(self, book_toc, title, curl, anchor_title, previous=None):
        self.__book_toc = book_toc
        self.__title = title
        self.__curl = curl
        self.__anchor_title = '' if anchor_title is None else anchor_title
        self.__previous = previous
        self.__next = None

    @property
    def book(self):
        return self.__book_toc.book

    @property
    def book_toc(self):
        return self.__book_toc

    @property
    def curl(self):
        return self.__curl

    @property
    def url(self):
        return self.__curl.url

    @property
    def title(self):
        return self.__title

    @property
    def anchor_title(self):
        return self.__anchor_title

    @property
    def as_anchor(self):
        if self.anchor_title:
            return f'<a href="{self.url}" title="{self.anchor_title}">{self.title}</a>'
        else:
            return f'<a href="{self.url}">{self.title}</a>'

    @property
    def as_a(self):
        return self.as_anchor

    @property
    def next(self):
        """Next chapter object"""
        return self.__next

    @property
    def previous(self):
        """Previous chapter object"""
        return self.__previous

    @property
    def prev(self):
        return self.previous

    def __set_next__(self, next_chapter):
        assert isinstance(next_chapter, self.__class__)
        assert self.__next is None
        self.__next = next_chapter

    def __str__(self):
        return self.as_anchor

    def __repr__(self):
        return repr(self.__str__())


class ChapterPart:
    def __init__(self, name=''):
        """if name is none then """
        assert isinstance(name, str)
        self._name = name
        self._chapter_lists = []

    def add_chapter_list(self, ch_list):
        assert isinstance(ch_list, ChapterList)
        self._chapter_lists.append(ch_list)

    @property
    def chapter_lists(self):
        return tuple(self._chapter_lists)

    def as_html(self, added_level=None):
        added_level = 0 if added_level is None else added_level
        header = '    ' * added_level + ('' if not self._name else
                                         f"<div class='book-toc-part-header'>{self._name}</div>")
        return \
            f'\n{header}\n' +\
            '\n'.join(chl.as_html(added_level=added_level) for chl in self._chapter_lists) + '\n'

    def __str__(self):
        return '\nPart: ' + self._name + '>\n' + '\n'.join(str(chl) for chl in self._chapter_lists)

    def __repr__(self):
        return repr(self.__str__())


class ChaptersTOC:
    def __init__(self, site, book_cpath, toc_cpath):
        self._site = site
        self.__book_cpath = book_cpath
        self.__chapter_parts = []
        self.__cpath_to_chapter = {}

        self.__toc_cpath = toc_cpath
        self.__toc_parent_cpath = self.__toc_cpath.parent_cpath

        # tmp
        self.__chapter_cpath_tuples = []

        self.__is_done = False

    @property
    def site(self):
        return self._site

    @property
    def book_cpath(self):
        return self.__book_cpath

    @property
    def book_curl(self):
        return self._site.object_manager.get_cfields(self.__book_cpath).curl

    @property
    def book_url(self):
        return self._site.object_manager.get_cfields(self.__book_cpath).curl.url

    @property
    def book_cfields(self):
        return self._site.object_manager.get_cfields(self.__book_cpath)

    @property
    def book(self):
        return self._site.object_manager.get_marked_content(self.__book_cpath)

    @property
    def chapter_cpaths(self):
        return tuple(self.__cpath_to_chapter.keys())

    def add_part(self, part):
        assert not self.__is_done
        assert isinstance(part, ChapterPart)
        self.__chapter_parts.append(part)

    def add_chapter(self, ch_link: ChLink):
        assert not self.__is_done
        assert isinstance(ch_link, ChLink)
        href = ch_link.link_src
        if href.startswith('/'):
            raise SynamicError(f'Chapter link must be relative: {href}')
        marked_extensions = self.site.system_settings['configs.marked_extensions'].as_tuple
        if not href.endswith(marked_extensions):
            raise SynamicError(f'Chapter link must be a relative path to a file with an extension of marked content'
                               f' {marked_extensions}: {href}')
        if href.endswith('/'):
            raise SynamicError(f'Chapter link must be a relative file name to a marked content: {href}')

        content_cpath = self.__toc_parent_cpath.join(href, is_file=True)
        if not content_cpath.exists():
            raise SynamicPathDoesNotExistError(
                f'CPath referred to by chapter link {href} does not exist: {content_cpath.abs_path}'
            )
        if content_cpath in self.__cpath_to_chapter:
            raise SynamicError(
                f'CPath referred to by chapter link {href} already added to the toc: {content_cpath.abs_path}'
            )

        # process chapter cpath
        prev_chapter = None if not self.__chapter_cpath_tuples else self.__chapter_cpath_tuples[-1][0]
        cfields = self._site.object_manager.get_cfields(content_cpath)
        if cfields is None:
            raise SynamicError(
                f'CFields not found for content path {content_cpath.relative_path}'
            )
        else:
            curl = cfields.curl
        chapter = Chapter(self, ch_link.link_text, curl, ch_link.link_title, previous=prev_chapter)
        if prev_chapter is not None:
            prev_chapter.__set_next__(chapter)
        self.__chapter_cpath_tuples.append((chapter, content_cpath))
        self.__cpath_to_chapter[content_cpath] = chapter

        return chapter

    def get_chapter(self, cpath, default=None):
        return self.__cpath_to_chapter.get(cpath, default)

    def __on_mutation_done__(self):
        assert not self.__is_done

        # delete temporaries
        del self.__chapter_cpath_tuples

        self.__is_done = True

    def get_cpath_chapter_map(self):
        return self.__cpath_to_chapter.copy()

    @property
    def parts(self):
        return tuple(self.__chapter_parts)

    def get_last_part(self):
        if self.__chapter_parts:
            return self.__chapter_parts[-1]
        else:
            return None

    def as_html(self, added_level=None):
        added_level = 0 if added_level is None else added_level
        res = []
        for ch_part in self.__chapter_parts:
            res.append(
                ch_part.as_html(added_level=added_level)
            )
        return '\n'.join(res)

    def __str__(self):
        return '\n'.join(str(part) for part in self.__chapter_parts)

    def __repr__(self):
        return repr(self.__str__())


if __name__ == '__main__':
    text = \
"""
* chapter 1
    - [Sub Chapter 1](/go1)
    - Subchapter 2 whithout link
        * sub under sub 2
        * another sub under sub 2
- [Chapter 2](/ch2)
- Ch 1 Pt 2

1. ch p none
    - sub ch p none
        - more sub ch p none
- And this

"""
    p = MarkedChapterParser(None, text)
    toc = p.parse()
    print()
    # for p in toc.parts:
    #     print(p)
    print(toc.as_html(added_level=1))
