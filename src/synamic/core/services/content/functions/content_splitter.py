import re


def content_splitter(file_path, content_text):
    front_matter_sep = re.compile(r'^(?P<sep>-{3,})[ \t]*$')
    lines = content_text.splitlines()
    front_matter_lines = []
    body_lines = []

    fm_start_idx = None
    fm_end_idx = None
    sep = None
    idx = 0
    for line in lines:
        if fm_start_idx is None and fm_end_idx is None:
            front_matter_match = front_matter_sep.match(line)
            if line.strip() == '':
                # skip
                # before front matter
                idx += 1
                continue
            elif front_matter_match:
                sep = front_matter_match.group('sep')
                fm_start_idx = idx
            else:
                raise Exception('Invalid text before front matter section started. '
                                'Parsing error at line %d. File name: %s' % (idx + 1, file_path.relative_path))
        elif fm_start_idx is not None and fm_end_idx is None:
            # inside front matter.
            sep_end_text = line.strip()
            if sep_end_text == sep:
                fm_end_idx = idx
            else:
                front_matter_lines.append(line)
        elif fm_start_idx is not None and fm_end_idx is not None:
            # inside body
            body_lines.append(line)
        else:
            raise Exception('Parsing error at line %d. File name: %s' % (idx + 1, file_path.relative_path))
        idx += 1
    if fm_start_idx is None or fm_end_idx is None:
        raise Exception('Front matter section was not found. File name: %s' % file_path.relative_path)

    return '\n'.join(front_matter_lines), '\n'.join(body_lines)
