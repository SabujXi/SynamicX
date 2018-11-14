from jinja2 import BaseLoader, TemplateNotFound


class SynamicJinjaFileSystemLoader(BaseLoader):
    def __init__(self, site):
        self.__site = site

    def get_source(self, environment, template):
        site_id_sep = self.__site.synamic.sites.get_id_sep()
        template_dir = self.__site.system_settings['dirs.templates.templates']
        site = self.__site
        path_tree = site.path_tree
        template_cdir = path_tree.create_dir_cpath(template_dir)
        template_cfile = template_cdir.join(template, is_file=True)
        if template.startswith(site_id_sep):
            # only load from the current site.
            template_fn = template[len(site_id_sep):]
            template_cfile = template_cdir.join(template_fn, is_file=True)
            if not template_cdir.exists() or not template_cfile.exists():
                raise TemplateNotFound(
                    template,
                    message=f"Template "
                            f"{template_cfile.abs_path} does not exits for site with id {site.id.as_string}"
                )
        else:
            while site.has_parent:
                site = site.parent
                path_tree = site.path_tree
                template_cdir = path_tree.create_dir_cpath(template_dir)
                template_cfile = template_cdir.join(template, is_file=True)
                if template_cdir.exists() and template_cfile.exists():
                    break

            if not template_cdir.exists() or not template_cfile.exists():
                raise TemplateNotFound(
                    template,
                    message=f"Template "
                            f"{template_cfile.abs_path} does not exits for site with id {site.id.as_string}"
                )
        with template_cfile.open('r', encoding='utf-8') as f:
            source = f.read()
        last_gmtime = template_cfile.getmtime()

        return source, template_cfile.abs_path, lambda: template_cfile.getmtime() == last_gmtime

