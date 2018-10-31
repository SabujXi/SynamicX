"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


class _SiteSettings:
    def __init__(self, site, syd):
        self.__site = site
        self.__syd = syd

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
        value = self.__syd.get(dotted_key, default=default)
        if value == default:
            # try in system
            value = self.__site.default_configs.get('settings').get(dotted_key, default)
        return value

    def __getitem__(self, item):
        value = self.get(item, None)
        if value is None:
            raise KeyError('Key `%s` in settings was not found' % str(item))
        else:
            return value

    def __getattr__(self, key):
        value = self.get(key, None)
        if value is None:
            raise AttributeError('Attribute `%s` in settings was not found' % str(key))
        else:
            return value

    def __contains__(self, item):
        res = self.get(item, None)
        if res is None:
            return False
        else:
            return True

    def __str__(self):
        return str(self.__)

    def __repr__(self):
        return repr(self.__str__())


class SiteSettingsService:
    def __init__(self, site):
        self.__site = site

    def load(self):
        pass

    def make_site_settings(self):
        system_settings_syd = self.__site.default_configs.get('settings')
        dirs_syd = self.__site.default_configs.get('dirs')
        configs_syd = self.__site.default_configs.get('configs')

        om = self.__site.object_manager
        fn = 'settings.syd'
        user_syd = om.get_syd(fn)
        new_syd = system_settings_syd.new(dirs_syd, configs_syd, user_syd)

        return new_syd
