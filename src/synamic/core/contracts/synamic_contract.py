from abc import abstractmethod, ABCMeta


class SynamicContract(metaclass=ABCMeta):
    @abstractmethod
    def load(self):
        pass

    @property
    @abstractmethod
    def event_system(self):
        pass

    @property
    @abstractmethod
    def urls(self):
        pass

    @property
    @abstractmethod
    def urls(self):
        pass

    @property
    @abstractmethod
    def tags(self):
        pass

    @property
    @abstractmethod
    def categories(self):
        pass

    @property
    @abstractmethod
    def menus(self):
        pass

    @abstractmethod
    def register_path(self, dir_path):
        pass

    @abstractmethod
    def register_virtual_file(self, virtual_file):
        pass

    @property
    @abstractmethod
    def is_loaded(self):
        pass

    @property
    @abstractmethod
    def path_tree(self):
        pass

    @property
    @abstractmethod
    def templates(self):
        pass

    @property
    @abstractmethod
    def type_system(self):
        pass

    @property
    @abstractmethod
    def model_service(self):
        pass

    @property
    @abstractmethod
    def content_service(self):
        pass

    @property
    @abstractmethod
    def site_settings(self):
        pass

    @property
    @abstractmethod
    def taxonomy(self):
        pass

    @property
    @abstractmethod
    def series(self):
        pass

    @abstractmethod
    def add_content(self, content):
        pass

    @abstractmethod
    def add_document(self, document):
        pass

    @abstractmethod
    def add_auxiliary_content(self, document):
        pass

    @property
    @abstractmethod
    def dynamic_contents(self):
        pass

    @abstractmethod
    def add_static_content(self, file_path):
        pass

    @abstractmethod
    def get_document_by_id(self, mod_name, doc_id):
        pass

    @abstractmethod
    def get_url(self, parameter):
        pass

    @abstractmethod
    def get_content_by_content_url(self, curl):
        pass

    @property
    @abstractmethod
    def site_root(self):
        pass

    @property
    @abstractmethod
    def content_dir(self):
        pass

    @property
    @abstractmethod
    def template_dir(self):
        pass

    @property
    @abstractmethod
    def meta_dir(self):
        pass

    @property
    @abstractmethod
    def models_dir(self):
        pass

    @property
    @abstractmethod
    def settings_file_name(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def initialize_site(self, force=False):
        pass

    @abstractmethod
    def filter_content(self, filter_txt):
        pass




