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


class ContentUrlContract(abc.ABC):
    """
        For YAML provided urls
            curl can be of string or another map.
            eg:
                curl: /my/path/to/file
            or:
                curl:
                    curl: /my/path/to/file
                    name: my_awesome_url_name  # this name must conform to identifier as in variables

            - a '/' will be added at the end of the urls if it is not there.
    """
    @property
    @abc.abstractmethod
    def absolute_url(self):
        """
            With the scheme and domain and path 
        """
        pass

    @property
    @abc.abstractmethod
    def path(self):
        """
        Root relative path
        Normalized path"""
        pass

    @property
    @abc.abstractmethod
    def generalized_path(self):
        """Generalized/lower path"""
        pass

    @property
    @abc.abstractmethod
    def generalized_real_path(self):
        """Generalized/lower real path"""
        pass

    @property
    @abc.abstractmethod
    def url_encoded_path(self):
        """
        :return: curl-encoded version of path
         
         Note: to_file_system_path does not need this because they do need to be present in html.
        """

    @property
    @abc.abstractmethod
    def real_path(self):
        """
        Must all, including this path, be normalized.
        
        e.g:
            path: me/one
            to_file_system_path: me/one/index.html
        
        e.g2:
            path: me/one/hi.html
            to_file_system_path: me/one/hi.html  # <the same>
        """

    @property
    @abc.abstractmethod
    def dir_components(self):
        """
            split to_file_system_path, not path, by forward slash '/'
            BUT this depends on is_file.
            If it is_file then the basename of it will be excluded
            
            Purpose:
                For creating directory depending on the array returned by this.
            
            Returns:
                A list or another ordered iterable.
        """

    @property
    @abc.abstractmethod
    def is_file(self):
        """
            is the resource, generated or static, indicates a file or directory
        """

    @property
    @abc.abstractmethod
    def is_dir(self):
        pass

    # @property
    # @abc.abstractmethod
    # def content(self):
    #     """
    #         Urls are associated only with some kind of content.
    #          This will return the content object (maybe, so that we can call render() on it later)
    #     """

    @property
    @abc.abstractmethod
    def to_file_path(self):
        """
            Must return a file name with os.sep specific to the running platform 
        """

    @abc.abstractmethod
    def create_auxiliary_url(self):
        pass
