import os
from pprint import pprint
from synamic.core.parsing_systems.curlybrace_parser import Syd
from synamic.core.synamic import Synamic
from synamic.core.object_manager import ObjectManager


def bootstrap(site_root):
    # Environment Variables

    # read settings file.
    settings_file_name = 'settings.syd'
    settings_full_fn = os.path.join(site_root, settings_file_name)
    with open(settings_full_fn, encoding='utf-8') as f:
        text = f.read()

    # > debug delete: settings value display.
    settings_syd = Syd(text, None).parse()
    for key, value in settings_syd.items():
        print(key, ' => ', value)

    print('\n ---- Syd __str__ ----- \n')
    pprint(settings_syd)
    # < debug delete

    # testing dirs default config interpolation
    print(' ----- dirs.syd interpolation')
    fn = os.path.join('A:\MyProjects\PersonalProjects\AdvancedSiteGenerator\Synamic\src\synamic\core\configs\dirs.syd')
    with open(fn) as f:
        text = f.read()
    dirs_tree = Syd(text, None).parse()
    print(dirs_tree.value)

    synamic = Synamic(site_root)
    synamic.load()
    om = ObjectManager(synamic)
