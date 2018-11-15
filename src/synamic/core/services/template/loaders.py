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

    def get_source(self, environment, template):
        site_id_sep = self.__site.synamic.system_settings['configs.site_id_sep']
        template_dir = self.__site.system_settings['dirs.templates.templates']
        site = self.__site
        template_name_match = template_name_pat.match(template)
        site_id = template_name_match.group('site_id')
        template_name = template_name_match.group('path')

        # only load from the current site.
        if site_id == site_id_sep:
            site = self.__site
        elif site_id is not None:
            site_id_obj = self.__site.synamic.sites.make_id(site_id)
            try:
                site = self.__site.synamic.sites.get_by_id(site_id_obj)
            except KeyError:
                raise SynamicSiteNotFound(
                    f'Site with id {site_id} was not found when looking for templated named {template} ->'
                    f' {template_name} inside of it.'
                )
        else:
            path_tree = site.path_tree
            template_cdir = path_tree.create_dir_cpath(template_dir)
            template_cfile = template_cdir.join(template, is_file=True)

            while True:
                path_tree = site.path_tree
                template_cdir = path_tree.create_dir_cpath(template_dir)
                template_cfile = template_cdir.join(template, is_file=True)
                if template_cfile.exists():
                    break
                else:
                    if site.has_parent:
                        site = site.parent
                        continue
                    else:
                        break
        path_tree = site.path_tree
        template_cdir = path_tree.create_dir_cpath(template_dir)
        template_cfile = template_cdir.join(template_name, is_file=True)

        if not template_cfile.exists():
            raise TemplateNotFound(
                template,
                message=f"Template "
                        f"{template_cfile.abs_path} does not exits for site with id {site.id.as_string}"
            )

        with template_cfile.open('r', encoding='utf-8') as f:
            source = f.read()
        last_gmtime = template_cfile.getmtime()
        return source, template_cfile.abs_path, lambda: template_cfile.getmtime() == last_gmtime
