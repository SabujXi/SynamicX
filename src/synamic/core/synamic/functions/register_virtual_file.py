from synamic.core.exceptions.synamic_exceptions import SynamicException
from synamic.core.classes.virtual_file import VirtualFile


def synamic_register_virtual_file(synamic, virtual_file, registered_virtual_files):
    self = synamic

    assert type(virtual_file) is VirtualFile
    if virtual_file in registered_virtual_files:
        raise SynamicException("Virtual file (%s) already exists" % virtual_file.file_path)
    registered_virtual_files.add(virtual_file)
