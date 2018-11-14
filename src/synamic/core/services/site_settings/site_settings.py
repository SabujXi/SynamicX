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
        self.__site_address = None

    @property
    def site_address(self):
        if self.__site_address is None:
            # calculate dev server address when dev server running.
            if self.__site.synamic.dev_params.get('host', None):
                dev_params = self.__site.synamic.dev_params
                host_scheme = 'http'
                hostname = dev_params.get('host')
                port = str(dev_params.get('port', '8080'))
                port_str = f':{port}'
                host_base_path_str = ''
                site_address = host_scheme + "://" + hostname + port_str + host_base_path_str
            # calculate from settings/configs
            else:
                site_address = self.get('site_address', None)
                if site_address is None:
                    host_port = self['host_port']
                    host_scheme = self['host_scheme']
                    hostname = self['hostname']
                    host_base_path = self['host_base_path'].strip('/')
                    port_str = f':{host_port}' if host_port else ''
                    host_base_path_str = f'{host_base_path}'
                    site_address = host_scheme + "://" + hostname + port_str + host_base_path_str
            self.__site_address = site_address
        else:
            site_address = self.__site_address
        return site_address

    @property
    def origin_syd(self):
        return self.__syd

    def get(self, dotted_key, default=None):
        value = self.__syd.get(dotted_key, default=default)
        if value == default:
            # try in system
            value = self.__site.system_settings.get(dotted_key, default)
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
        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True

    def make_site_settings(self):
        system_settings = self.__site.system_settings

        # all parent settings are merged
        parent_settings_syd = []
        site = self.__site
        while site.has_parent:
            parent_settings_syd.append(
                self.__site.parent.settings.origin_syd
            )
            site = site.parent
        parent_settings_syd.reverse()

        # site specific settings and private settings.
        site_om = self.__site.object_manager
        site_settings_cfile = self.__site.path_tree.create_file_cpath('settings.syd')
        site_settings_private_cfile = self.__site.path_tree.create_file_cpath('settings.private.syd')
        if site_settings_cfile.exists():
            parent_settings_syd.append(
                site_om.get_syd(site_settings_cfile)
            )
        if site_settings_private_cfile.exists():
            parent_settings_syd.append(
                site_om.get_syd(site_settings_private_cfile)
            )

        # construct final syd
        new_syd = system_settings.new(*parent_settings_syd)
        # construct site settings object
        site_settings = _SiteSettings(self.__site, new_syd)
        return site_settings
