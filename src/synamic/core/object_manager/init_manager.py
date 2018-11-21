class InitManager:
    def __init__(self, synamic):
        self.__synamic = synamic

    def init_site(self, cpath):
        assert cpath.is_dir
        dir_cpaths, file_cpaths = cpath.list_cpaths(respect_settings=False)
        if dir_cpaths or file_cpaths:
            print(f'The path {cpath.abs_path} is not empty. Init\'ing failed.')
            return False
        system_settings = self.__synamic.system_settings

        # gitignore
        cpath.join('.gitignore', is_file=True).\
            write_text(
            f'settings.private.syd\n'
            f'{system_settings["dirs.outputs.outputs"]}\n'
            f''
        )

        # settings
        cpath.join('settings.syd', is_file=True).\
            write_text('')

        # contents directory
        contents_cdir = cpath.join(system_settings['dirs.contents.contents'], is_file=False)
        contents_cdir.makedirs()
        contents_cdir.\
            join(system_settings['configs.dir_meta_file_name']).\
            write_text('type: post\n')
        contents_cdir.join('home.md', is_file=True).write_text(
'''
---
title: Welcome to Synamic
path: /
template: default.html
id: home
---

# Welcome to Synamic
This is your home page.

'''
        )

        # templates
        templates_cdir = cpath.join(system_settings['dirs.templates.templates'], is_file=False)
        templates_cdir.makedirs()
        templates_cdir.join('.gitkeep', is_file=True).make_file()
        templates_cdir.join('default.html', is_file=True).\
            write_text(
'''
<!doctype html>
<html>
    <head> <title> {{ content.title }} </title> </head>
    <body>
        {{ content.body.as_markup }}
    </body>
</html>
'''
        )

        # configs dir
        configs_cdir = cpath.join(system_settings['dirs.configs.configs'], is_file=False)
        configs_cdir.makedirs()
        configs_cdir.join('.gitkeep', is_file=True).make_file()

        # sites
        sites_cdir = cpath.join(system_settings['dirs.sites.sites'], is_file=False)
        sites_cdir.makedirs()
        sites_cdir.join('.gitkeep', is_file=True).make_file()

        # meta dirs
        metas_cdir = cpath.join(system_settings['dirs.metas.metas'], is_file=False)
        metas_cdir.makedirs()

        data_cdir = cpath.join(system_settings['dirs.metas.data'], is_file=False)
        markers_cdir = cpath.join(system_settings['dirs.metas.markers'], is_file=False)
        menus_cdir = cpath.join(system_settings['dirs.metas.menus'], is_file=False)
        models_cdir = cpath.join(system_settings['dirs.metas.models'], is_file=False)
        users_cdir = cpath.join(system_settings['dirs.metas.users'], is_file=False)

        # data
        data_cdir.makedirs()
        data_cdir.join('links.syd', is_file=True).write_text(
            '''
google: http://google.com
facebook: http://facebook.com
            '''
        )

        # markers
        markers_cdir.makedirs()
        markers_cdir.join('categories.syd', is_file=True).write_text(
            '''
title: Categories
type: hierarchical
marks:[
    {
        title: Programming
        id: programming
        description: Programming Category

        marks:[
            {
                title: C
                id: programming-c
                description: Programming C Category
            }
        ]
    }
    {
        title: Web Development
        id: web-development
        description: Web Development Category
        ext: ext-web-development
    }
    {
        title: Web Design
        id: web-design
        description: Web Design Category
        ext: ext-web-design
    }
    {
        title: Internet Marketing
        id: internet-marketing
        description: Internet Marketing Category
        ext: ext-internet-marketing
    }
    
    {
        title: Career
    }
]

            '''
        )
        markers_cdir.join('tags.syd', is_file=True).write_text(
            '''
title: Tags
type: multiple
slug: topic
marks:[
    {
        title: Marketing
        id: marketing
        description: Marketing Tag
    }
    {
        title: Design
        id: design
        description: Design Tag
    }
    {
        title: Programming
        id: programming
        description: Programming Tag
    }
    
    {
        title: Career
    }
]
            '''
        )
        markers_cdir.join('type.syd', is_file=True).write_text(
            '''
title: Type
type: single
is_public: 0
marks: [
    {
        title: Post
        id: post
        description: Post Type
    }
    {
        title: Page
        id: page
        description: Page Type
    }
    {
        title: Series
        id: series
    }
]

            '''
        )

        # menus
        menus_cdir.makedirs()
        menus_cdir.join('primary.syd', is_file=True).write_text(
            '''
menus [
    {
        title: Welcome Home
        link: url://id:home

        menus: [
            {
                title: Menu nested to another level.
                link: #
            }
        ]
    }
    {
        title: External Link
        link: https://www.sabuj.me
    }

]
            '''
        )

        # models
        models_cdir.makedirs()
        models_cdir.join('.gitkeep').make_file()

        # users
        users_cdir.makedirs()
        users_cdir.join('user1.syd').\
            write_text(
            '''
name: User One
title: User One's Profile

description ~ {
    User 1 is a very active user on this website.
}
            '''
        )

        return True
