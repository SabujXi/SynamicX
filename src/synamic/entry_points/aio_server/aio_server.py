import os
from synamic.core.synamic import Synamic
from aiohttp import web
from .synamic_handler import synamic_handler

app = web.Application()
app.router.add_route('GET', '/{tail:.*}', synamic_handler)


def serve(root_dir: str, host='localhost', port='8080'):
    assert os.path.exists(root_dir)

    # bootstrap(site_root)
    synamic = Synamic(root_dir)
    synamic.set_dev_params(host=host, port=port)
    synamic.load()
    #  synamic.sites.load()
    app.synamic = synamic
    web.run_app(app, host=host, port=port)
