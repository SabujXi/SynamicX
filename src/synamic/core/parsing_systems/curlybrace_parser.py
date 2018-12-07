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
from synamic.core.standalones.functions.date_time import DtPatterns, parse_date, parse_time, parse_datetime
from synamic.core.standalones.syd import SydDataType, SydData, SydContainer
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


class SydParseError:
    def __init__(self, line, line_no, invalid_data, col_no=None, msg=''):
        self.line = line
        self.line_no = line_no
        self.invalid_data = invalid_data
        self.col_no = col_no
        self.msg = msg


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
            parent_container = SydContainer(key, is_list=is_list)
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
            cnt = SydContainer(key, is_list=True)
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

            data = SydData(key, '\n'.join(processed_lines), SydDataType.string)
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
                    data = SydData(key, res, SydDataType.string)
                # double quoted string
                else:  # text.startswith('"'):  # and text.endswith('"'):
                    content = text[1:]
                    res, text, _ = cls.__double_q_string(content)
                    res = res.replace(r'\n', '\n')
                    res = res.replace(r'\r', '\r')
                    res = res.replace(r'\t', '\t')
                    data = SydData(key, res, SydDataType.string)

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
                    data = SydData(key, number, SydDataType.number)
                # date-time match
                elif datetime_match:
                    dt_instance = parse_datetime(datetime_match)
                    data = SydData(key, dt_instance, SydDataType.datetime)
                # date match
                elif date_match:
                    date_instance = parse_date(date_match)
                    data = SydData(key, date_instance, SydDataType.date)

                # time match
                elif time_match:
                    time_instance = parse_time(time_match)
                    data = SydData(key, time_instance, SydDataType.time)
                # bare string : last resort
                else:
                    bare_string = data_part
                    if len(bare_string) > 1:
                        if bare_string[0:2] in (r'\(', r'\{', r'\['):
                            bare_string = bare_string[2:]
                    bare_string = bare_string.strip()
                    data = SydData(key, bare_string, SydDataType.string)

            data_list.append(data)
            text = text.strip()

        if len(data_list) == 0:
            # bare string
            data_list.append(
                SydData(key, '', SydDataType.string)
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


