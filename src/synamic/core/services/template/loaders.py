import re
from jinja2 import BaseLoader, TemplateNotFound
from synamic.exceptions import SynamicSiteNotFound

template_name_pat = re.compile(
    r"""^(?P<site_id>(
                        [^\s:/\\]+(~[^\s:/\\]+)+|~[^\s:/\\]+|~
                     )/
          )?
        (?P<path>.+)"""
    , re.VERBOSE)
# sync ~ in pattern system_settings['configs.site_id_sep']


class SynamicJinjaFileSystemLoader(BaseLoader):
    def __init__(self, site):
        self.__site = site

    def get_template_cfile(self, template_name):
        template = template_name
        system_settings = self.__site.synamic.system_settings
        site_settings = self.__site.settings

        site_id_sep = system_settings['configs.site_id_sep']
        default_theme_id = site_settings.get('themes.default', None)

        site = self.__site

        _template_name_match = template_name_pat.match(template)
        site_id = _template_name_match.group('site_id')
        template_name = _template_name_match.group('path')

        sites_up = []
        # only load from the current site.
        if site_id == site_id_sep:
            site = self.__site
            sites_up.append(site)
        elif site_id is not None:
            site_id_obj = self.__site.synamic.sites.make_id(site_id)
            try:
                site = self.__site.synamic.sites.get_by_id(site_id_obj)
                sites_up.append(site)
            except KeyError:
                raise SynamicSiteNotFound(
                    f'Site with id {site_id} was not found when looking for templated named {template} ->'
                    f' {template_name} inside of it.'
                )
        else:
            sites_up.append(site)
            while site.has_parent:
                site = site.parent
                sites_up.append(site)

        assert len(sites_up) > 0
        found = False
        for site in sites_up:
            path_tree = site.path_tree
            template_cdir = site.cpaths.templates_cdir
            template_cfile = template_cdir.join(template_name, is_file=True)
            if default_theme_id:
                default_template_cfile = template_cdir.join(default_theme_id, is_file=False).join(template_name,
                                                                                                  is_file=True)
                if default_template_cfile.exists():
                    template_cfile = default_template_cfile
                    found = True
                    break
            if template_cfile.exists():
                found = True
                break

        if not found:
            raise TemplateNotFound(
                template,
                message=f"Template "
                        f"{template_cfile.abs_path} does not exits for site with id {site.id.as_string}"
            )
        return template_cfile

    def get_source(self, environment, template):
        template_cfile = self.get_template_cfile(template)
        with template_cfile.open('r', encoding='utf-8') as f:
            source = f.read()
        last_gmtime = template_cfile.getmtime()
        return source, template_cfile.abs_path, lambda: template_cfile.getmtime() == last_gmtime
