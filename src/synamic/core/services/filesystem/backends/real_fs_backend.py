import os
import os.path
from synamic.core.contracts import BaseFsBackendContract
from synamic.exceptions import SynamicFSError


class FileSystemBackend(BaseFsBackendContract):
    def open(self, path, *args, **kwargs):
        try:
            fo = open(path, *args, **kwargs)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during opening path {path}):\n'
                f'{str(e)}'
            )
        return fo

    def exists(self, path):
        try:
            res = os.path.exists(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during exists() on path {path}):\n'
                f'{str(e)}'
            )
        return res

    def is_file(self, path):
        try:
            res = os.path.isfile(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during checking if the path is a file path {path}):\n'
                f'{str(e)}'
            )
        return res

    def is_dir(self, path):
        try:
            res = os.path.isdir(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during checking if the path is a directory path {path}):\n'
                f'{str(e)}'
            )
        return res

    def listdir(self, path):
        try:
            res = os.listdir(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during listing path: {path}):\n'
                f'{str(e)}'
            )
        return res

    def makedirs(self, path):
        try:
            res = os.makedirs(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during making directory with path: {path}):\n'
                f'{str(e)}'
            )
        return res

    def getmtime(self, path):
        try:
            res = os.path.getmtime(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during getmtime on path: {path}):\n'
                f'{str(e)}'
            )
        return res

    def getctime(self, path):
        try:
            res = os.path.getctime(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during getctime on path: {path}):\n'
                f'{str(e)}'
            )
        return res

    def remove(self, path):
        try:
            res = os.remove(path)
        except (OSError, IOError) as e:
            raise SynamicFSError(
                f'Synamic File System Error (occurred during remove on path: {path}):\n'
                f'{str(e)}'
            )
        return res
