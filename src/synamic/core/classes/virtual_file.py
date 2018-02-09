"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


from synamic.core.classes.path_tree import ContentPath2


class VirtualFile:
    def __init__(self, file_path: ContentPath2, file_content):
        assert file_path.is_file
        self.__file_content = file_content
        self.__file_path = file_path
        self.__is_written = False

    @property
    def file_path(self):
        return self.__file_path

    @property
    def file_content(self):
        return self.__file_content

    def write_to_file(self):
        if self.__is_written is True:
            raise Exception("File was already written")
        elif self.__file_path.exists():
            raise Exception("File already exists, cannot write to it")
        else:
            if type(self.__file_content) is str:
                file_content = self.__file_content.encode('utf-8')
            elif type(self.__file_content) is bytes:
                file_content = self.__file_content
            else:
                raise Exception("Incompatible type, cannot determine mode to write")
        with self.__file_path.open('wb', file_content) as f:
            f.write(file_content)

    def __eq__(self, other):
        return self.__file_path == other.__file_path

    def __hash__(self):
        return hash(self.__file_path)
