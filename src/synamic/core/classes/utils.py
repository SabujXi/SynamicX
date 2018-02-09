"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


class DictUtils:
    @staticmethod
    def get_or_create_dict(d: dict, inner_dict_key):
        """
        Checks if another dictionary inside the dictionary exists or not. If does not exist it creates one. In either
        case it returns the dict 
        """
        if inner_dict_key not in d:
            d[inner_dict_key] = dict()
        return d[inner_dict_key]
