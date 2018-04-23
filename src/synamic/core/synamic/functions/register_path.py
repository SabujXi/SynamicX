from synamic.core.exceptions.synamic_exceptions import SynamicException


def synamic_register_path(synamic, dir_path, registered_dir_paths):
    self = synamic

    assert dir_path.is_dir
    # print(self.__registered_dir_paths)
    if dir_path in registered_dir_paths:
        raise SynamicException(
            "The same path (%s) is already registered" % self.path_tree.get_full_path(dir_path.path_components))
    registered_dir_paths.add(dir_path)