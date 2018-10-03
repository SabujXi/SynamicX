"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import abc
import re


class BaseModuleContract(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self):
        pass

    @property
    @abc.abstractmethod
    def is_loaded(self):
        pass


class BaseMetaModuleContract(BaseModuleContract):
    pass


class BaseContentModuleContract(BaseModuleContract):
    pass