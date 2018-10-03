import os

# from synamic.core.builtin_event_handlers.handlers import handler_pre_build
from synamic.core.synamic._synamic_enums import Key


def _synamic_build(synamic, content_map, event_trigger):
    self = synamic
    out_path = self.path_tree.create_path(self.site_settings.output_dir)
    if not out_path.exists():
        self.path_tree.makedirs(out_path.path_components)

    # self.event_system.add_event_handler(
    #     EventTypes.PRE_BUILD,
    #     Handler(handler_pre_build)
    # )
    #
    # event_trigger(
    #     EventTypes.PRE_BUILD,
    #     Event(self)
    # )
    # ^ event section

    # real work begins
    self.initialize_site()
    old_contents = content_map[Key.CONTENTS_SET].copy()

    def build_content(process_content_map):
        for cont in process_content_map:
            url = cont.url_object
            dir = os.path.join(self.site_root, self.site_settings.output_dir, *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            with url.to_content_path.open('wb') as f:
                stream = cont.get_stream()
                f.write(stream.read())
                stream.close()
    build_content(old_contents)
    tertiary_contents = content_map[Key.CONTENTS_SET] - old_contents
    build_content(tertiary_contents)

