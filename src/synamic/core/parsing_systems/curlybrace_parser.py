# lots of thoughts needed.

"""
-------------------------------------------------------------------------
--------- comments -------------
// is a single line comment.
# is also a single line comment.
Where comments can appear:
1. Inside a block: on an independent line that does not contain scalar data
2. Inside a block list: on an independent line that does not contain scalar data
3. After the starting curly brace/bracket of block/list.
4. On an empty line outside of blocks/block lists. That is on the independent lines of file. Be noted that, a file is considered block and it
    Contains key value pairs.

Where it cannot appear:
Within or at the end of scalar data: string, number, date
Within or at the end of linear list: (a, t, 5)

Comments may be preceded by spaces and/or tabs.

\# is a literal hash. Hash inside strings are also literal hash.
\// is also literal two forward slash.
--------------------------------

--------- import/include --------
Other data files can also be imported/included with !include <relative file name with or without ext>

!include must be on it's own line.

--------- load model ------------
Models can be specified by the system
---------------------------------

--------- interpolation ---------
Interpolation happens in the second pass. So, after everything is loaded, the non-recursive keys can be found
easily.

{{ key }}

{{ key.subkey }}

key can be found in the current data file or from an included file.

To put literal {{ then just precede it with a single backward slash. \{{
This is not needed for single curly brace.

-------- escaping ----------------
Escaping is done through backward slash. Escaping are relaxed and special in synamic data file.
To escape a backward slash escape it with another one.
Escaping does not take place in each and every thing.
----------------------------------
---------- CALCEL, don't want to keep type hinting, need to make things clean for end user | data __document_types ----------
* Data type inforcement *
If you want to force type on a data then you can use the following key suffixes.
!n -> number
!i -> integer
!f -> float
!d -> date
!t -> time
!dt -> date-time
!s -> string
!l -> list
!b -> boolean

* Other suffixes can also be defined by the system with models *

1) >> Number: Priority Top (1) <<
-> 1 <- is a number.
-> 2.5 <- is a number.
# 1 & 1.0 are equal.

2) >> Date, Time & Datetime: Priority 2 <<
If something falls in the format of date, time or datetime that is considered is date.
The default formats are.

If you want a date like format to be treated like string then use quoted string.

Date: <4 digit year>:<1 or 2 digit month within the range of 1-12>:<1 or 2 digit date within the range defined by month>
Time: <1 or 2 digit hour within range of 0-23 or 0-12 if AM/PM present>:<1 or 2 digit minute 1-59>:<Optional: 1 or 2 digit seconds>:<Optional: AM/PM - case insensitive>
Datetime: Combination of date & time separated by space character(s) - spaces/tabs.

3) >> String: Priority 3 <<
-> Strings 1 (no quotation): strings does not need any quotation mark. No special/escape characters - everything is literal char.
key: this is a string value, leading and trailing spaces are ignored.

-> String 2 (single quotation): if the value part starts with a single quotation then it is considered single
quoted string. a quotation inside it must be escaped with backward slash. 

4) >> List: Priority 4
* If a key ends with "!l" or "!L" then it will be considered a list. So, there is no need to to delimit
list elements with [ & ]

- List elements are separated by commas. You cannot enforce type on list elements, they must be inferred.
- if you want special treatment then use model based parsing.

- List elements can contain numbers, single line strings, date, time, date-time, boolean data __document_types only.
- Strings must be single line strings. You can use multiline strings with triple quoting.

4) >> Other data: Priority 3 <<
If a key is mentioned in an associated model then the string is parsed.

 

--------------------------------
-------------------------------------------------------------------------


!include values-dev.txt
!include_if_exists values-super-dev2.txt

key1 : value
// data type specification cancelled: key10 !s the colon after the key is optional.
// data type specification cancelled: key11 !l : this is, a typed, key, with type list
key2 {
        multilevel: value 2
}

# multiline text: key must be suffixed with ~, in this case there must not be any type specifier.
# as described above, the colon is optional. But a multiline text must be enclosed in curly braces.
key3~: {

}

# if the there is no text after { then this empty line is not included in the output.
# if it contains some text then the preceding spaces are also considered to be included in the calculation of indentaion.

key30~ {
         Indentation does not start here.
  Indentation starts here.
  Tab normalization happens (no replace - just counted virtually) for counting indentation. One tab is considered
     as 4 spaces.
}

# if you do not want any indentation detection happen and take all the text literally, then you must use 
# double tilde.

key31~~ : {
   All preceded spaces are kept
Intact, no matter at how many level the key is nested.
}

# Nested values

key4: {  
    k1: {
         k11: value
    }
    k2: single line
    multiline~ {
    }
}
"""

import re
import enum
import pprint
import datetime
import numbers
from synamic.core.standalones.functions.date_time import DtPatterns, parse_date, parse_time, parse_datetime
from synamic.exceptions import SynamicSydParseError, get_source_snippet_from_text


# patterns
class _Patterns:
    key_pattern = re.compile(r'''^[ \t]*
            (?P<key>[a-zA-Z_]+[a-zA-Z0-9_]*) # key
            [ \t]*
            (?P<is_multiline>~{1,3})? # is multi line
            [ \t]*
            # data type specification cancelled (?P<type>![a-zA-Z0-9_]+)?[ \t]*    # enforced format. If it is specified in multiline code and no model is specified
                                   # then that format is ignored.
            :? # colon is optional
            (?={|\[|\s|\Z)
            ''', re.X)

    number = re.compile(r'^[ \t]*(?P<number>[+-]?[0-9]+(\.[0-9]+)?)[ \t]*$')
    date = DtPatterns.date
    time = DtPatterns.time
    datetime = DtPatterns.datetime

    inline_list_separator = re.compile(r'(?<!\\),')

    multiline_spaces = re.compile(r'^[ \t]*')

    inline_list = re.compile(r'^[ \t]*\((?P<content>.*?)\)[ \t]*$')

    interpolation_identifier = re.compile(r'(?<!\$)\$\{[ \t]*(?P<identifier>'
                                          r'[a-z_][a-z0-9_]*)[ \t]*\}', re.I)  # escape $ with another - that simple


class SydParseError:
    def __init__(self, line, line_no, invalid_data, col_no=None, msg=''):
        self.line = line
        self.line_no = line_no
        self.invalid_data = invalid_data
        self.col_no = col_no
        self.msg = msg


@enum.unique
class SydDataType(enum.Enum):
    number = 1
    date = 2
    time = 3
    datetime = 4
    string = 5

    # data structures
    # block = 6 # map
    # block_list = 7
    # inline_list = 8


syd_to_py_types = {
    SydDataType.time: (datetime.time, ),
    SydDataType.date: (datetime.date, ),
    SydDataType.datetime: (datetime.datetime, ),
    SydDataType.number: (numbers.Number, int, float),
    SydDataType.string: (str, )
}

py_to_syd_types = {}
for syd_type, py_types in syd_to_py_types.items():
    for py_type in py_types:
        py_to_syd_types[py_type] = syd_type


class __SydData:
    @property
    def is_scalar(self):
        return type(self) is SydScalar

    @property
    def is_container(self):
        return type(self) is SydContainer

    def syd_set_parent(self, p):
        raise NotImplemented

    def set_converter(self, c):
        raise NotImplemented

    def set_converted(self, v):
        raise NotImplemented

    @property
    def converter(self):
        raise NotImplemented


class SydScalar(__SydData):
    def __init__(self, key, value, datatype, parent_container=None, converter=None, converted_value=None):
        if key is not None:
            assert '.' not in key, f'Key {key} is invalid where value is {value}'
        assert isinstance(value, syd_to_py_types[datatype])
        self.__key = key
        self.__value = value
        self.__datatype = datatype
        self.__converter = converter
        self.__converted_value = converted_value
        self.__parent_container = None

        self.__cached_interpolated_str = None
        self.syd_set_parent(parent_container)

    def clone(self, parent_container=None, converter=None, converted_value=None):
        if converter is None:
            converter = self.__converter
        if converted_value is None:
            converted_value = self.__converted_value
        return self.__class__(self.__key, self.__value, self.__datatype, parent_container=parent_container, converter=converter, converted_value=converted_value)

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        if self.__converted_value is not None:
            value = self.__converted_value
        else:
            if not callable(self.__converter):
                value = self.__value
            else:
                value = self.__converter(self.__value)
                assert value is not None
                self.__value = value
        return value

    @property
    def value_origin(self):
        return self.__value

    def set_converted(self, value):
        assert value is not None
        self.__converted_value = value

    @property
    def type(self):
        return self.__datatype

    def syd_set_parent(self, p):
        assert type(p) in (SydContainer, type(None))
        self.__parent_container = p

        # process interpolation
        if p is not None:
            value = self.__value
            # process interpolation for string
            if self.__datatype is SydDataType.string:
                if self.__cached_interpolated_str is not None:
                    value = self.__cached_interpolated_str
                else:
                    value = self.__cached_interpolated_str = _Patterns.interpolation_identifier.sub(self.__interpolation_replacer,
                                                                                                    value)
            self.__value = value

    def set_converter(self, converter):
        assert not callable(self.__converter)
        self.__converter = converter

    @property
    def converter(self):
        return self.__converter

    def __str__(self):
        if self.key is not None:
            return "%s => %s" % (self.key, str(self.value))
        else:
            return str(self.value)

    def __repr__(self):
        return repr(self.__str__())

    def __interpolation_replacer(self, match):
        identifier = match.group('identifier')
        assert self.__key != identifier, 'Key is being interpolated recursively: %s' % identifier
        if self.__parent_container is not None:
            v = self.__parent_container.get(identifier, '')
            assert type(v) in (int, float, str), 'Only number and string data can be interpolated in' \
                                                 'to a string. Data with' \
                                                 ' kye `%s` is of type `%s`' % (self.key, str(type(v)))
            v = str(v)  # convert it in case it is a number.
            return v
        else:
            raise Exception('Parent for key `%s` is set to None' % str(self.__key))


class SydContainer(__SydData):
    def __init__(self, key, is_list=False, parent_container=None, converter=None, converted_value=None, read_only=False):
        self.__key = key
        self.__is_list = is_list
        self.__map = {}
        self.__list = []
        self.__parent_container = None  # parent_container from init will be set through a method below.
        self.__converter = converter
        self.__converted_value = converted_value
        self.__read_only = read_only

        self.syd_set_parent(parent_container)

    def clone(self, parent_container=None, converter=None, converted_value=None, read_only=False):
        if converter is None:
            converter = self.__converter
        if converted_value is None:
            converted_value = self.__converted_value
        cln = self.__class__(self.__key, self.__is_list, parent_container=parent_container, converter=converter, converted_value=converted_value, read_only=read_only)
        for e in self.__list:
            cln.add(e.clone())
        return cln
    copy = clone

    @property
    def is_root(self):
        return self.__parent_container is None or self.__key == '__root__' or self.__key is None

    # methods prefixed with syd_ are considered private functions or functions should not be used by users.
    def syd_clone_original_contents(self):
        l = []
        for e in self.__list:
            l.append(e.clone())
        return tuple(l)

    def syd_get_original(self, key, multi=False):
        assert isinstance(key, (int, str, list, tuple)), 'Only integer and string keys are accepted, you provide key of type: %s' % str(
            type(key))
        key = int(key) if type(key) is str and key.isdigit() else key

        if type(key) is int:
            assert self.is_list, "Index %d provided for a block collection. Use numeric index only for list collections" % key
            try:
                d = self.__list[key]
                if multi:
                    d = (d, )

            except IndexError:
                raise IndexError('%d does not exist')
        else:
            if isinstance(key, (list, tuple)):
                keys = key
            else:
                keys = key.split('.')
            try:
                first_key = keys[0]
                cont_tuple = tuple(t[1] for t in self.__map[first_key])
                keys = keys[1:]
                last_idx = len(keys) - 1
                for idx, _key in enumerate(keys):
                    if last_idx == idx:
                        if not cont_tuple[-1].is_container:
                            # print('Found value is not a block - it is a scalar')
                            raise KeyError('Found value is not a block - it is a scalar')
                    _ = cont_tuple[-1].syd_get_original(_key, multi=multi)

                    if multi:
                        cont_tuple = _
                    else:
                        cont_tuple = (_, )

                if multi:
                    d = cont_tuple
                else:
                    d = cont_tuple[-1]
            except KeyError:
                raise KeyError('Key `%s` was not found' % key)
        return d

    # def copy_

    @property
    def is_list(self):
        return self.__is_list

    @property
    def key(self):
        return self.__key

    def keys(self):
        l = list()
        for e in self.__list:
            if e.key is not None:
                l.append(e.key)
        return tuple(l)

    def values(self):
        """Values are not converted!!!"""
        l = list()
        for e in self.__list:
            value = e.value
            l.append(value)
        return tuple(l)

    def items(self):
        """Values are not converted!!!"""
        l = []
        i = 0
        for e in self.__list:
            value = e.value
            if self.is_list:
                l.append((i, value))
            else:
                l.append((e.key, value))
            i += 1
        return tuple(l)

    def __getitem__(self, key):
        value = self.get(key, default=None, multi=False)
        if value is None:
            raise KeyError('Key `%s` was not found' % key)
        return value

    def set_converter(self, converter):
        assert not callable(self.__converter)
        assert not self.is_root
        self.__converter = converter

    def set_converter_for(self, key, converter):
        syds = self.syd_get_original(key, multi=True)
        for syd in syds:
            syd.set_converter(converter)

    def get(self, key, default=None, multi=False):
        try:
            value = self.syd_get_original(key, multi=multi)
            if not multi:
                value = value.value
            else:
                values = value
                _ = []
                for v in values:
                    _.append(v.value)
                value = tuple(_)
        # except (KeyError, IndexError, AssertionError):
        except (KeyError, IndexError):
            value = default
        return value

    def add(self, syd):
        assert not self.__read_only
        self.__list.append(syd)
        if not self.is_list:
            idx = len(self.__list) - 1
            key = syd.key
            if key not in self.__map:
                l = []
                self.__map[key] = l
            else:
                l = self.__map[key]
            l.append((idx, syd))
        syd.syd_set_parent(self)

    def set(self, key, py_value):
        """
        Sets py value as converted to existing key
        BUT for non existing value it creates scalar of only allowed type.
        """
        assert not self.__read_only
        try:
            syd = self.syd_get_original(key, multi=False)
            syd.set_converted(py_value)
        except KeyError:
            if '.' not in key:
                parent_container = self
            else:
                comps = key.split('.')[:-1]
                parent_container = self.syd_get_original(comps, multi=False)
                assert parent_container.is_container

            syd_scalar = SydScalar(
                key,
                py_value,
                py_to_syd_types[type(py_value)],
                converter=None,
                converted_value=py_value
            )
            parent_container.add(syd_scalar)

    def __setitem__(self, key, value):
        assert not self.__read_only
        self.set(key, value)

    def __remove__from__self(self, key):
        key = int(key) if type(key) is str and key.isdigit() else key
        if self.is_list:
            del self.__list[key]
        else:
            idx_syd_l = self.__map[key]
            idx_syd_l.reverse()

            del self.__map[key]
            for idx, syd in idx_syd_l:
                del self.__list[idx]

            new_map = type(self.__map)()
            for idx, e in enumerate(self.__list):
                if e.key not in new_map:
                    l = []
                    new_map[e.key] = l  # Here was that deadly bug
                else:
                    l = new_map[e.key]
                l.append((idx, e))
            self.__map = new_map

    def __delitem__(self, key):
        assert not self.__read_only
        assert type(key) in (int, str), 'Only integer and string keys are accepted, you provide key of type: %s' % str(
            type(key))
        key = str(key)
        ks = key.split('.')
        key2del = ks[-1]
        ks = ks[:-1]

        try:
            if len(ks) == 0:
                cont = self
            else:
                k = ks[0]
                ks = ks[1:]
                cont = self.syd_get_original(k)
                for k in ks:
                    cont = cont._get_original(k)
            cont.__remove__from__self(key2del)
        except (KeyError, IndexError):
            raise KeyError('Key/Index `%s` was not found' % key)

    def __contains__(self, key_value):
        """This method only checks for existence of a key - not value, even if this object is a list"""
        if self.is_list:
            value = key_value
            return value in self.__list
        else:
            key = key_value
            res = self.get(key, None)
            return False if res is None else True

    def key_exists(self, key):
        return key in self

    @property
    def value(self):
        if self.__converted_value is not None:
            value = self.__converted_value
        else:
            if not callable(self.__converter):
                value = self.value_origin
            else:
                value = self.__converter(self.value_origin)
                assert value is not None
                self.__converted_value = value
        return value

    @property
    def value_origin(self):
        if self.is_list:
            c = []
            for a in self.__list:
                c.append(a.value)
            c = tuple(c)
        else:
            # c = collections.OrderedDict()
            c = {}
            for a in self.__list:
                c[a.key] = a.value
        return c

    def set_converted(self, value):
        assert value is not None
        assert not self.is_root
        self.__converted_value = value

    def new(self, *others):
        assert not self.is_list, 'Cannot create new from list, it must be a block'
        self_clone = self.clone()
        for other in others:
            assert not other.is_list, 'Cannot create new with list, need block'
            for oe in other.syd_clone_original_contents():
                if oe.key in self_clone:
                    del self_clone[oe.key]
                self_clone.add(oe)
        return self_clone

    def __str__(self):
        l = []
        for e in self.__list:
            l.append(str(e))
        if self.is_list:
            data_text = ", ".join(l)
        else:
            data_text = "\n".join(l)
        if self.key is not None:
            return str(self.key) + " { %s }" % data_text
        else:
            res = "{ %s }" % data_text
            return res

    def __repr__(self):
        return repr(self.__str__())

    def syd_set_parent(self, p):
        assert type(p) in (type(None), self.__class__), 'Invalid type: %s' % str(type(p))
        self.__parent_container = p

    @property
    def converter(self):
        return self.__converter


@enum.unique
class _ParseState(enum.Enum):
    processing_block = 1
    processing_list = 1.1
    processing_block_string = 3  # multiline string
    processing_inline = 2
    processing_inline_list = 2.2
    processing_nothing = 0

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)


class SydParser:
    def __init__(self, text, debug=False):
        self.__text = text
        self.__debug = debug
        self.__tree = SydContainer('__root__')
        self.__error = None
        self.__lines = self.__text.splitlines()
        self.__current_line_no = 0

        self.__parse_states = []
        self.__container_stack = [self.__tree]

    def __dprint(self, *args, **kwargs):
        if self.__debug:
            print(*args, **kwargs)

    @property
    def __fmt_error_msg(self):
        line = self.__lines[self.__current_line_no - 1]
        return f"Line no: {self.__current_line_no}\n"\
            f"Line: {line}\nCurrent Processing States Stack: {', '.join(str(state) for state in self.__parse_states)}"

    def __enter_state(self, state: _ParseState):
        self.__parse_states.append(state)

    def __leave_state(self, state: _ParseState):
        assert type(state) is _ParseState
        assert self.__parse_states[-1] == state
        self.__parse_states.pop()

    def __leave_last_state(self):
        self.__parse_states.pop()

    @property
    def __current_state(self):
        if len(self.__parse_states) == 0:
            return _ParseState.processing_nothing
        return self.__parse_states[-1]

    @property
    def __current_level(self):
        return len(self.__parse_states)

    def parse(self):  # (-1)
        if len(self.__lines) != 0:
            assert self.__current_line_no == 0
            self.__enter_state(_ParseState.processing_block)
            self.__process_block('__root__')  # root doc is considered a single block.
            self.__leave_state(_ParseState.processing_block)
        return self.__tree

    def __process_block(self, key, block_type=None):  # (0)
        """This loop is used at the root and at any nested level (root from that perspective)"""
        assert self.__current_state in (_ParseState.processing_block, _ParseState.processing_list)
        if key != '__root__':
            if self.__current_state == _ParseState.processing_list:
                is_list = True
            else:
                is_list = False
            parent_container = SydContainer(key, is_list)
            root_container = self.__container_stack[-1]
            root_container.add(parent_container)
            self.__container_stack.append(parent_container)

        while self.__current_line_no < len(self.__lines):
            # this top level while lool will process only the top level lines/key-values
            self.__current_line_no += 1
            line = self.__lines[self.__current_line_no - 1]
            self.__dprint("Line %s: %s" % (self.__current_line_no, line))

            # ignore empty line: empty lines are ignored only when they are at the top level (no matter how indented)
            stripped_line = line.strip()
            if stripped_line == '':
                continue
            # ignore comment
            elif self.__is_comment(stripped_line):
                continue
            # leave block
            is_block_end, block_end_type = self.__block_end(line)
            if is_block_end:
                if block_type == '{':
                    if block_end_type == '}':
                        # self.current_line_no += 1
                        break
                elif block_type == '[':
                    if block_end_type == ']':
                        # self.current_line_no += 1
                        break
            self.__process_block_items()
        del self.__container_stack[-1]

    def __process_key_value(self):
        pass

    def __process_value(self):
        pass

    def __process_block_items(self):  # (1)
        line = self.__lines[self.__current_line_no - 1]
        #  text = line
        #  extract key
        if self.__current_state in (_ParseState.processing_list, _ParseState.processing_block_string):
            key = None
            end_pos = 0
            is_multiline = False
            multiline_token = None
        else:
            key_match = _Patterns.key_pattern.match(line)
            if key_match:
                key = key_match.group('key')
                end_pos = key_match.end()
                multiline_token = key_match.group('is_multiline')
                if multiline_token:
                    is_multiline = True
                else:
                    is_multiline = False
            else:
                self.__dprint("error in line: %s" % line)
                err = SynamicSydParseError(
                    f'Syd Parsing key match error:\n{self.__fmt_error_msg}\n'
                    f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                )
                raise err

        # self.__dprint("\nKEY: %s" % str(key))
        # self.__dprint("\nLINE END: %s" % line[end_pos:])
        # process multi line block
        # multi line string processing

        line_end = line[end_pos:].lstrip()
        next_line = self.__next_line
        is_block_start, block_type = self.__block_start(line_end, next_line)
        inline_list_match = _Patterns.inline_list.match(line_end)
        if is_multiline:
            # end_pos += multiline_match.end()
            self.__enter_state(_ParseState.processing_block_string)
            self.__process_datum_ml_string(end_pos, key, multiline_token)
            self.__leave_state(_ParseState.processing_block_string)
        # so it is not a multi line stuff
        # is it nested stuff?
        elif is_block_start:
            if block_type == '{':
                self.__enter_state(_ParseState.processing_block)
                # self.current_line_no += 1
                self.__process_block(key, block_type)
                #
                self.__leave_state(_ParseState.processing_block)
            elif block_type == '[':
                self.__enter_state(_ParseState.processing_list)
                self.__process_block(key, block_type)
                self.__leave_state(_ParseState.processing_list)
            else:
                err = SynamicSydParseError(
                    f'Syd Parsing error - Something is horribly wrong:\n{self.__fmt_error_msg}\n'
                    f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                )
                raise err
        # inline list
        elif inline_list_match:
            content = inline_list_match.group('content')
            cnt = SydContainer(key, True)
            self.__container_stack[-1].add(cnt)
            self.__container_stack.append(cnt)
            self.__enter_state(_ParseState.processing_inline_list)
            parts = self.__process_datum_inline(content, None, True)
            for part in parts:
                cnt.add(part)
            self.__leave_state(_ParseState.processing_inline_list)
            del self.__container_stack[-1]
        elif self.__is_inline(line_end, next_line):
            self.__enter_state(_ParseState.processing_inline)
            data = self.__process_datum_inline(line_end, key)
            self.__container_stack[-1].add(data)
            # must not increment as it it is inline: X self.current_line_no += 1
            self.__leave_state(_ParseState.processing_inline)
        else:
            err = SynamicSydParseError(
                f'Syd Parsing error - could not parse:\n{self.__fmt_error_msg}\n'
                f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
            )
            raise err

    def __process_datum_ml_string(self, end_pos, key, multiline_token):  # (1.1)
        line = self.__lines[self.__current_line_no - 1]
        line_end = line[end_pos:].lstrip()
        if not line_end.startswith('{'):
            err = SynamicSydParseError(
                f'Syd Parsing error - ...:\n{self.__fmt_error_msg}\n'
                f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
            )
            raise err
        else:
            lines = []
            line_end = line_end[1:]

            # test & ignore first line if valid code follows (starts with {)
            if line_end.strip() == '' or self.__is_comment(line_end):
                pass  # ignore empty line or comment for the first line.
            else:
                err = SynamicSydParseError(
                    f'Syd Parsing error - Multiline string starting line cannot contain data (only comment or blank)'
                    f':\n{self.__fmt_error_msg}\n'
                    f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                )
                raise err

            # now collect lines until you get a } on a single line.
            # if a line contains only one } and you want to make that literal then escape it with \
            # extract lines
            while True:
                self.__current_line_no += 1
                line = self.__lines[self.__current_line_no - 1]
                is_block_end, end_char = self.__block_end(line)
                if is_block_end and end_char == '}':
                    break
                if line.strip(' \t') == r'\}':
                    # unescape starting curly brace.
                    line = line.replace(r'\}', '}')

                lines.append(line)
                if self.__current_line_no == len(self.__lines):
                    err = SynamicSydParseError(
                        f'Syd Parsing error - End of text but no end to the newline found'
                        f':\n{self.__fmt_error_msg}\n'
                        f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                    )
                    raise err

                    # process lines
                    # > if is_multiline == '~~'
                    # blah blah blah
            if multiline_token == '~':
                processed_lines = []
                ind_sizes = []
                for line in lines:
                    match = _Patterns.multiline_spaces.match(line)
                    spaces = match.group() if match.group() is not None else ''
                    size = 0
                    for space in spaces:
                        if space == ' ':
                            size += 1
                        elif space == '\t':
                            size += 4
                    ind_sizes.append(size)
                if len(ind_sizes) > 0:
                    ind_size = min(ind_sizes)
                else:
                    ind_size = 0

                # process lines.
                for line in lines:
                    idx = 0
                    ind_limit = 0
                    for char in line:
                        while ind_limit < ind_size:
                            if char == ' ':
                                ind_limit += 1
                            elif char == '\t':
                                ind_limit += 4
                            else:
                                break
                            idx += 1
                    res_line = line[idx:]
                    processed_lines.append(res_line)
            elif multiline_token == '~~':
                processed_lines = lines
            else:
                assert multiline_token == '~~~'
                processed_lines = lines
                # TODO: process for escape chars & special sequences.

            data = SydScalar(key, '\n'.join(processed_lines), SydDataType.string)
            self.__container_stack[-1].add(data)

    def __process_datum_inline(self, text, key, processing_inline_list=False):
        try:
            return self.convert_to_scalar_values(text, key, processing_inline_list=processing_inline_list)
        except ValueError as ve:
            err = SynamicSydParseError(
                f'Syd Parsing error - value error ({ve.args[0]}):\n{self.__fmt_error_msg}\n'
                f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
            )
            raise err

    @staticmethod
    def __extract_key(text):
        match = _Patterns.key_pattern.match(text)
        if not match:
            return None
        key = match.group('key')
        return key

    @staticmethod
    def __is_comment(line):
        """ Is this LINE a comment"""
        # print(repr(line.splitlines()))
        assert len(line.splitlines()) == 1
        line = line.lstrip(' \t')
        if line.startswith('#') or line.startswith('//'):
            return True
        return False

    def __is_inline(self, text, next_line):
        if next_line is None:
            return True
        is_block_start, _ = self.__block_start(text, next_line)
        if is_block_start:
            return False
        else:
            return True

    def __block_start(self, text, next_line):
        """A multiline is a block. A nested group is also a block"""
        lstripped_text = text.lstrip(' \t')
        if lstripped_text.startswith('{') or \
                lstripped_text.startswith('['):
            # is the rest comment
            text_end = lstripped_text[1:]
            text_end_stripped = text_end.strip(' \t')
            if (text_end_stripped == '' or
                    self.__is_comment(text_end)) and \
                    next_line is not None:
                # so this is a block
                return True, lstripped_text[0]
            else:
                err = SynamicSydParseError(
                    f'Syd Parsing error - Something is horribly wrong!:\n{self.__fmt_error_msg}\n'
                    f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                )
                raise err
        return False, None

    @staticmethod
    def __block_end(line):
        stripped_line = line.strip(' \t')
        if stripped_line == '}':
            return True, '}'
        elif stripped_line == ']':
            return True, ']'
        return False, None

    @property
    def __next_line(self):
        next_line = None
        if self.__current_line_no < len(self.__lines):  # current line is the last line:
            next_line = self.__lines[self.__current_line_no]
        return next_line

    #  InlineDataProcessors
    single_quoted_string_stop = re.compile(r"(?<!\\)'")
    double_quoted_string_stop = re.compile(r'(?<!\\)"')

    @classmethod
    def __single_q_string(cls, line):
        return cls.__quoted_string(line, "'")

    @classmethod
    def __double_q_string(cls, line):
        return cls.__quoted_string(line, '"')

    @classmethod
    def __quoted_string(cls, line, q):
        assert q in ("'", '"')
        res = ''
        end_pos = 0

        if q == '"':
            m = cls.double_quoted_string_stop.search(line)
        else:
            m = cls.single_quoted_string_stop.search(line)

        if not m:
            res += line
            end_pos = len(line)
        else:
            start = line[:m.end() - 1]
            res += start
            end_pos += m.end()
        res = res.replace(r"\%s" % q, "%s" % q)
        end = line[end_pos:]
        return res, end, end_pos

    @classmethod
    def convert_to_scalar_values(cls, text, key, processing_inline_list=False):
        data_list = []
        text = text.strip(' \t\r\n')

        while text:
            # single quoted string
            if text.startswith(("'", '"')):
                if text.startswith("'"):  # and text.endswith("'"):
                    content = text[1:]
                    res, text, _ = cls.__single_q_string(content)
                    data = SydScalar(key, res, SydDataType.string)
                # double quoted string
                else:  # text.startswith('"'):  # and text.endswith('"'):
                    content = text[1:]
                    res, text, _ = cls.__double_q_string(content)
                    res = res.replace(r'\n', '\n')
                    res = res.replace(r'\r', '\r')
                    res = res.replace(r'\t', '\t')
                    data = SydScalar(key, res, SydDataType.string)

                if processing_inline_list:
                    next_comma_match = _Patterns.inline_list_separator.search(text)
                    if next_comma_match:
                        next_stop = next_comma_match.end()
                        text = text[next_stop:]
                else:
                    if text.strip() != '':
                        err = SynamicSydParseError(
                            f'Syd Parsing error - We are not processing inline list, but still there are some data left'
                            f' after converting one:\n{self.__fmt_error_msg}\n'
                            f'Details:\n{get_source_snippet_from_text(self.__text, self.__current_line_no, limit=10)}'
                        )
                        raise err
            else:
                orig_end = text
                next_stop = len(text)
                data_part = text[:next_stop]
                text = text[next_stop:]
                if processing_inline_list:
                    next_comma_match = _Patterns.inline_list_separator.search(orig_end)
                    if next_comma_match:
                        next_stop = next_comma_match.end()
                        data_part = orig_end[:next_stop - 1]
                        text = orig_end[next_stop:]
                data_part = data_part.strip()

                number_match = _Patterns.number.match(data_part)
                datetime_match = _Patterns.datetime.match(data_part)
                date_match = _Patterns.date.match(data_part)
                time_match = _Patterns.time.match(data_part)

                # number
                if number_match:
                    num_str = number_match.group('number')
                    if num_str.startswith(('+', '-')):
                        sign = num_str[0]
                        num_str = num_str[0:]
                        sign_mul = 1 if sign == '+' else -1
                    else:
                        sign_mul = 1
                    if data_part.isdigit():
                        number = int(data_part)
                    else:
                        number = float(data_part)
                    number = number * sign_mul
                    data = SydScalar(key, number, SydDataType.number)
                # date-time match
                elif datetime_match:
                    dt_instance = parse_datetime(datetime_match)
                    data = SydScalar(key, dt_instance, SydDataType.datetime)
                # date match
                elif date_match:
                    date_instance = parse_date(date_match)
                    data = SydScalar(key, date_instance, SydDataType.date)

                # time match
                elif time_match:
                    time_instance = parse_time(time_match)
                    data = SydScalar(key, time_instance, SydDataType.time)
                # bare string : last resort
                else:
                    bare_string = data_part
                    if len(bare_string) > 1:
                        if bare_string[0:2] in (r'\(', r'\{', r'\['):
                            bare_string = bare_string[2:]
                    bare_string = bare_string.strip()
                    data = SydScalar(key, bare_string, SydDataType.string)

            data_list.append(data)
            text = text.strip()

        if len(data_list) == 0:
            # bare string
            data_list.append(
                SydScalar(key, '', SydDataType.string)
            )

        if processing_inline_list:
            return data_list
        else:
            return data_list[0]

    @classmethod
    def covert_one_value(cls, text):
        syd_scalar = cls.convert_to_scalar_values(text, '__null__', processing_inline_list=False)
        return syd_scalar.value


if __name__ == '__main__':
    text = """
    a : {
        what are you doing
    }
    ml ~ {
        my
         text
    }
    ml2 t
    k : v
    m : n
    ikndf /lj
    key1{
        key_n1 : {
            k: 1
            l m
            o {
                p ; l:9;
            } 
        }
    }
    key2: key2data
    list: (uj, 87   ,     ll)
    
        listn: ((8\, 7))
    str2qu: "double quoted string"
    str1qu: 'single quoted string'
    num: 5.4
    lis1[#
    my name
        
        yes
        ali
        {
            k: v
        }
        ("l" ,           7')
        (    7,   8)
        "JJJ Hye"
        ~{
        ml srting in list
            got it?
        }
    ]
    lis1{
        k m
    }
    """
    text2 = """
    max1: 5
    lis1: xx
    """
    s = SydParser(text, None, debug=True)
    s2 = SydParser(text2, None, debug=True)
    print("--- parsing ----")
    tree = s.parse()
    tree2 = s2.parse()
    ntree = tree.new(tree2)
    print("--- the tree ---")
    print(tree)
    # print(SpecialTokens.tokens)
    print('--- pyvalue ---\n')
    pprint.pprint(tree.value)
    # print('--- is collection ---\n')
    # pprint.pprint(tree.is_collection)
    # print('--- keys ---\n')
    # pprint.pprint(tree.keys())
    print('--- get multi ---\n')
    pprint.pprint(tree.get('lis1', multi=True))
    print('--- ... in ... ---\n')
    pprint.pprint('lis1.3' in tree)

    print(' --------- tree.new tree2')
    print(ntree)


