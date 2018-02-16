from synamic.core.classes.path_tree import ContentPath2
from synamic.core.classes.virtual_file import VirtualFile


class NullService:
    def __init__(self, cfg):
        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root, (cfg.settings_file_name,), is_file=True),
                ''
            )
        )

        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root, ('.synamic',), is_file=True),
                ''
            )
        )

        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root,
                             (
                                 *cfg.templates.service_home_path.path_components,
                                 'default.html'
                             ),
                             is_file=True),
"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Default Synamic Template</title>
  </head>
  <body>
    <h1>This is the default synamic template. Provide your own template within content fields or in 
    parent meta fields to meet your demands</h1>
    <hr/>
    
    {% if content %}
        <h1>
            {{ content.title }}
        </h1>
        <hr/>
            {{ content.body.as_markup }}
    {% endif %}
  </body>
</html>
"""
            )
        )

        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root,
                             (
                                 *cfg.model_service.service_home_path.path_components,
                                 'default.model.txt'
                             ),
                             is_file=True),
"""
title:
    _type: text
    unique: no

created_on:
    _type: datetime

updated_on:
    _type: datetime

tags:
    _type: taxonomy.tags

__body__:
    _type: markdown
"""
            )
        )

        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root,
                             (
                                 *cfg.content_service.service_home_path.path_components,
                                 '.meta.txt'
                             ),
                             is_file=True),
"""
slug: /
template: default.html
"""
            )
        )

        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root,
                             (
                                 *cfg.content_service.service_home_path.path_components,
                                 'home.md'
                             ),
                             is_file=True),
"""
====
title: Home Page Sample: The Journey of a Code Craftsman - Md. Sabuj Sarker
id: home-en
permalink: /
tags: x, y
created_on: 2017-12-23 22:45:10 AM
language: en
====
This is a sample home page content for synamic.

"""
            )
        )
