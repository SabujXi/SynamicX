import enum


@enum.unique
class Key(enum.Enum):
    CONTENTS_BY_ID = 0
    CONTENTS_BY_CONTENT_URL = 3
    CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH = 5
    CONTENTS_SET = 4
    DYNAMIC_CONTENTS = 6