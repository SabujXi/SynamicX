from synamic.core.new_parsers.document_parser import FieldParser


class SiteSettings:
    __default_values = {
        'output_dir': '_html',
        'host_scheme': 'http',
        'hostname': 'example.com',
        'host_port': '',
        'host_base_path': '/'
    }

    def __init__(self, config):
        self.__config = config

        fn = config.settings_file_name
        if config.path_tree.exists(fn):
            _root_f = FieldParser('').parse()
        else:
            with config.path_tree.open_file(fn, encoding='utf-8') as f:
                text = f.read()
            _root_f = FieldParser(text).parse()
        self.__root_field = _root_f

    @property
    def host_address(self):
        host_address = self.get('host_address', None)
        if host_address is not None:
            host_port = self.host_port
            host_base_path = self.host_base_path
            if self.host_port and host_base_path != '/':
                host_address = self.hostname_scheme + "://" + self.hostname + ':' + host_port + '/'
            elif self.host_port:
                host_address = self.hostname_scheme + "://" + self.hostname + ':' + host_port
            else:
                assert bool(host_base_path)
                host_address = self.hostname_scheme + "://" + self.hostname + ':' + host_port + (
                    host_base_path if host_base_path.startswith('/') else host_base_path
                )
        return host_address

    def get(self, dotted_key, default=None):
        field = self.__root_field.get(dotted_key, default=default)
        if field == default:
            return default
        elif field is None:
            return None
        else:
            if field.is_single:
                return field.value
            else:
                d = field.to_dict_ordinary()
                return d

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, key):
        self.get(key)

    def __contains__(self, item):
        res = self.get(item, None)
        if res is None:
            return False
        else:
            return True

    def __str__(self):
        return str(self.__root_field.to_dict_ordinary())

    def __repr__(self):
        return repr(self.__str__())
