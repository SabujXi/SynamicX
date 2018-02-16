"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import re
from collections import deque
from collections import OrderedDict
import pprint
from synamic.core.exceptions.synamic_exceptions import *
"""Example DOC: #s are comments
========
key: value x y z value - single line key value

multi_line_key:
----
here is the multiline value
here is line one
----
another_value: here it is another value
another_value: here it is another value
========
the rest is document content
"""

"""ForMenu like nested systems:
# field types:
# 1. Single line field
# 2. Multiline field

field:
    field:  # value cannot be here for fields that have multiple values 4 keeping things unambiguous
        list_of_values: | this will |, | build |, | an |, | ordered |, | list |
        # * there is no concept of list of values in this system. The above string will directly be given inside field, now it's 
        # * programmers' responsibility how they implement the listing thing
        key1: |but |
        key2: this
        key3: will
        key4: be
        key5: key-value
        more_nested~:
            ---
            but this is a 
            multiline value
            the preceding white spaces are stripped off
            ---
            # there cannot be a list of multiline values - it's only available for single line values
            
# anything that starts with a hash (optionally preceded
# by any number of spaces/tabs

# if you want to keep leading and preceding spaces of 
# a value then quote enclose the whole value within pipe |, and later parse that
# then how to put a literal pipe:
# the start and end quote only matters, anything between them are literal
# so, no escaping crap needed.
# again, if there is either start or end pipe then they are literal pipes
# TODO: modelling and mapping type to nested fields
# TODO: value interpolation and dependency checking in fields
"""


class _Pat:

    line_breaker = re.compile(r'^\r\n|\n|\r', re.MULTILINE)
    field_linear_value = re.compile(r"^(?P<field_name>[_a-z]+[_a-z0-9]*)?\s*:\s*(?P<single_value>.+)?\s*$", re.I)
    field_multiline_value = re.compile(r"^(?P<field_name>[_a-z]+[_a-z0-9]*)?\s*~\s*:", re.I)  # everything after ~: is skipped

    frontmatter = re.compile(r'^\s*(={4,})(\r\n|\n|\r)(?P<fields_txt>.*?)\1(\r\n|\n|\r)', re.I|re.MULTILINE|re.DOTALL)


class DocumentParser:
    def __init__(self, txt):
        self.__txt = txt

        self.__body = None
        self.__fields = None
        self.__root_field = None
        self.__parsing_complete = False

    @property
    def body(self):
        assert self.__parsing_complete is True
        return self.__body

    @property
    def fields(self):
        assert self.__parsing_complete is True
        return self.__fields

    @property
    def root_field(self):
        return self.__root_field

    def parse(self):
        assert self.__parsing_complete is False
        m_frontmatter = _Pat.frontmatter.match(self.__txt)
        if not m_frontmatter:
            # print("No, frontmatter found")
            root_f = Field(-1, '__root__')
            self.__root_field = root_f
            self.__fields = tuple()
            self.__body = self.__txt
        else:
            root_f = FieldParser(m_frontmatter.group('fields_txt')).parse()
            self.__root_field = root_f
            self.__fields = tuple(root_f.children)
            self.__body = self.__txt[m_frontmatter.end():]
        del self.__txt
        self.__parsing_complete = True
        return self

    def __str__(self):
        fields_str = (str(f) for f in self.fields)
        fs = "FIELDS: \n------\n" + "\n".join(fields_str)
        bs = "BODY: : \n------\n" + self.body
        return fs + bs

    def __repr__(self):
        return repr(self.__str__())


class FieldParser:
    def __init__(self, txt):
        self.__txt = txt.strip()
        self.__parsing_complete = False

    @staticmethod
    def char_count_for_level(levels, line):
        """
        Solving the gotcha of tab and space mixing.
        returns: how many character to skip for getting desired value
        """
        # print("Line for count level: %s" % line)
        char_count = 0
        skip_a_cycle = False
        for level in range(levels):
            # print('Level np: %s and line %s' % (level, line))
            if skip_a_cycle:
                skip_a_cycle = False
                continue
            if line[char_count] == '\t':  # one tab is two nesting level as 1tab=8spaces
                skip_a_cycle = True
                char_count += 1
            elif line[char_count:char_count + 4] == ' ' * 4:
                char_count += 4
            else:
                # print(line)
                raise ParsingError('Syntax error or indentation issue. Multiline value must align with '
                                'indentation', line_no=line)
        return char_count

    @staticmethod
    def guess_nesting_level_for_field(line):
        m = re.match(r'^(?P<whitespaces>\s*)[a-z_][a-z0-9_]*\s*~?\s*:', line, re.I)
        if not m:
            raise Exception("No field pattern found: `%s`" % line)
        whitespaces = m.group('whitespaces')
        if whitespaces == '':
            return 0
        levels = 0
        char_idx = 0
        while char_idx < len(whitespaces):
            if whitespaces[char_idx] == '\t':  # one tab is two nesting level as 1tab=8spaces
                levels += 2
            elif whitespaces[char_idx:char_idx + 4] == ' ' * 4:
                levels += 1
                char_idx += 4
            else:
                raise Exception('Invalid level - unlike to happen this error')
        return levels

    @staticmethod
    def skip_blanks_to(line_no, lines):
        # print("Line no to skip from: %s" % line_no)
        while line_no < len(lines):
            line = lines[line_no]
            if line.strip() == '':
                line_no += 1
                # print('>>>skipping line: %s' % line)
            else:
                break
        return line_no

    def parse(self):
        # print("Parsing started...")
        assert self.__parsing_complete is False, "Cannot call parse again, save value"
        fields_stack = deque()
        fields_stack.append(Field(-1, '__root__'))

        if self.__txt.strip() == '':
            return fields_stack[-1]

        lines = _Pat.line_breaker.split(self.__txt)
        # print(lines)

        line_no = 0
        nesting_level = 0

        while line_no < len(lines):
            _line = lines[line_no]
            # print("line-no:%s, nesting_level:%s\n%s" % (line_no, nesting_level, _line))

            #  skip chars for nesting level
            char_count = self.char_count_for_level(nesting_level, _line)
            string_to_process = _line[char_count:]

            # field and single_value match
            m_field_linear_value = _Pat.field_linear_value.match(string_to_process)
            m_field_multiline_value = _Pat.field_multiline_value.match(string_to_process)

            must_have_nested_fields_next = False

            if m_field_linear_value:
                field_name = m_field_linear_value.group('field_name')
                single_value = m_field_linear_value.group('single_value')

                if single_value is None:
                    field_has_nested_fields = True
                else:
                    field_has_nested_fields = False
                    field_value = single_value

                # print("?Field has nested fields?: %s" % field_has_nested_fields)

                if field_has_nested_fields:
                    f = Field(nesting_level, field_name)
                    fields_stack[-1].add(f)
                    fields_stack.append(f)
                    # print("Line: %s" % _line)
                    must_have_nested_fields_next = True
                    line_no += 1
                else:
                    f = Field(nesting_level, field_name, field_value)
                    fields_stack[-1].add(f)
                    # will not add to stack and will not increment nesting level as no new nesting level introduced
                    line_no += 1
            elif m_field_multiline_value:
                field_name = m_field_multiline_value.group('field_name')

                value_lines = []
                nesting_level += 1

                line_no += 1
                if line_no >= len(lines):
                    raise Exception("Unexpected end of lines, invalid syntax")
                next_line = lines[line_no]
                char_count = self.char_count_for_level(nesting_level, next_line)
                string_to_process = next_line[char_count:]
                m_dashes = re.match('^-{3,}', string_to_process)
                if not m_dashes:
                    raise Exception('At least three dashes could not be found so that the value can be processed')
                dashes = m_dashes.group()

                while True:
                    line_no += 1
                    if line_no >= len(lines):
                        raise Exception("Unexpected end of lines, invalid syntax")
                    next_line = lines[line_no]
                    char_count = self.char_count_for_level(nesting_level, next_line)
                    string_to_process = next_line[char_count:]
                    if string_to_process.strip() == dashes:
                        break
                    value_lines.append(string_to_process)
                field_value = "\n".join(value_lines)

                f = Field(nesting_level, field_name, field_value)
                fields_stack[-1].add(f)
                # will not add to stack and will not increment nesting level as no new nesting level introduced
                line_no += 1

                nesting_level -= 1
            else:
                raise Exception("Error parsing fields")

            # print("At the end of one field processing line %s" % line_no)

            # skip blank lines
            line_no = self.skip_blanks_to(line_no, lines)

            # print("Skipped to line no %s" % line_no)

            # predict next line level
            if line_no < len(lines):
                next_line = lines[line_no]
                # print('Next Line: %s' % next_line)

                new_nesting_level = self.guess_nesting_level_for_field(next_line)

                if must_have_nested_fields_next:
                    assert new_nesting_level == nesting_level + 1, "The next nesting level (%s) is not up to the expectation to current (%s)" % (new_nesting_level, nesting_level)
                    nesting_level += 1
                else:
                    # print("New level: `%s`, Nesting level: `%s`" % (new_nesting_level, nesting_level))
                    if nesting_level != new_nesting_level:
                        assert new_nesting_level < nesting_level, "Without having nested fields, nesting can only go backward"
                        diff = nesting_level - new_nesting_level
                        for count in range(diff):
                            fields_stack.pop()
                        nesting_level = new_nesting_level

        self.__parsing_complete = True
        # print(fields_stack[0])
        # input()
        return fields_stack[0]


class Field:
    def __init__(self, at_level, field_name, value=None):
        assert type(field_name) is str
        self.__at_level = at_level
        self.__field_name = field_name
        self.__value = value
        self.__values_map = OrderedDict()
        self._multiple_values_map = OrderedDict()

    def add(self, another_field):
        assert self.__value is None, "This field has single value, so you cannot add children. The value is `%s`" % self.__value
        name = another_field.name
        if name in self.__values_map:
            list_4_multiple = self._multiple_values_map.get(name, None)
            if list_4_multiple is None:
                list_4_multiple = self._multiple_values_map[name] = []
            list_4_multiple.append(another_field)
        else:
            self.__values_map[another_field.name] = another_field

    def get(self, dotted_name, default=None):
        names = dotted_name.split('.')
        if len(names) == 1:
            field = self.__values_map.get(names[0], None)
            if field is None:
                return default
            else:
                return field
        else:
            idx = 0
            for name in names:
                if idx == 0:
                    field = self.__values_map.get(name, None)
                else:
                    field = field.get(name, None)
                if field is None:
                    return default
                idx += 1
            return field

    def get_multi(self, dotted_name, default=None):
        names = dotted_name.split('.')
        parent_field = self
        if len(names) == 1:
            field = self.__values_map.get(names[0], None)
        else:
            # idx = 0
            for name in names:
                # if idx == 0:
                field = parent_field.get(name, None)
                # else:
                # field = field.get(name, None)
                if field is None:
                    parent_field = None
                    break
                parent_field = field
                # idx += 1

        res = default
        if field is not None:
            if parent_field is not None:
                fields_in_mulit = parent_field._multiple_values_map.get(field.name, None)

                if fields_in_mulit is None:
                    res = (field,)
                else:
                    res = (field, *fields_in_mulit)
                    # print(len(res))
        return res

    @property
    def is_root(self):
        if self.__at_level == -1:
            return True
        return False

    def to_dict(self):
        __children__ = []
        m = {
            'name': self.name,
            'value': self.value,
        }

        if self.__values_map:
            for field in self.__values_map.values():
                __children__.append(field.to_dict())
        if __children__:
            m['__children__'] = tuple(__children__)
        return m

    def to_dict_ordinary(self):
        """
        {
            name: value
            name2: {
                xname: value
            }
        } 
        """
        d = OrderedDict()
        for field_name, field in self.__values_map.items():
            name = field_name
            value = field.value
            if value is None:
                value = field.to_dict_ordinary()
            d[name] = value
        return d

    def to_dict_flat(self):
        """Just the immediate first level data as dict"""
        d = OrderedDict()
        for field_name, field in self.__values_map.items():
            name = field_name
            value = field.value
            d[name] = value
        return d

    @property
    def name(self):
        return self.__field_name

    @property
    def value(self):
        return self.__value

    @property
    def children(self):
        return tuple(self.__values_map.values())

    @property
    def children_map(self):
        return self.__values_map.copy()

    @property
    def has_children(self):
        return True if self.__value is None else False

    @property
    def flat_fields(self):
        """
        This will take children,
        then it will take only the child who are single values (not having any nested child)
        and return another Field instance - so it will be OK to call a_field.value from there.
        """
        fv = self.__class__(-1, '__flat_values__')
        for child in self.__values_map.items():
            if child.is_single:
                fv.add(
                    Field(0, child.name, child.value)
                )
        return fv

    @property
    def level(self):
        return self.__at_level

    @property
    def pos(self):
        return self.__at_pos

    def visit(self, visitor, res_map, field_path=None):
        field_path = () if field_path is None else (*field_path,)
        if self.is_root:
            for field in self.children:
                # field_path.extend(field_path); field_path.append(field.name)
                field.visit(visitor, res_map, (*field_path, field.name))
        else:
            if not self.has_children:
                proceed = visitor(self, field_path, res_map)
                if not proceed:
                    return res_map
            else:
                for field in self.children:
                    field.visit(visitor, res_map, (*field_path, field.name))
        return res_map

    def __bool__(self):
        return self.value is not None and self.children_map is not None

    def __getattr__(self, key):
        raise AttributeError('Could not find `%s`' % key)

    def __getitem__(self, item):
        return self.get(item)

    def __str__(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return repr(self.__str__())

test_txt = """
====
field01:
    field0101:  
        list_of_values: | this will |, | build |, | an |, | ordered |, | list |

        key1: |but |
        key2: this
        key3: will
        key4: be
        key5: key-value
        more_nested~:
            ---
            but this is a 
            multiline value
            the preceding white spaces are stripped off
            ---
another_field: 1
more_field1: hey yo yo...

====
Body here.
end

next a newline

"""


def test():
    d = DocumentParser(test_txt)
    p = d.parse()
    # p = FieldParser(test_txt)
    # f = p.parse()
    print(p)

if __name__ == '__main__':
    test()
