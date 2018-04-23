"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import http.server
import re
from urllib.parse import unquote

from synamic.core.urls.url import ContentUrl


class SynamicDevServerRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        cfg = self.server.synamic_config
        paths = self.path.split("?")
        if len(paths) > 1:
            path = "".join(paths[:-1])
            print("self.path %s and path %s" % (self.path, path))
        else:
            path = self.path

        if re.match(r'/?--sys--/?$', path):
            self.send_response(200, message="Ok")
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <body>
                <br/><br/><br/>
                <a href="/--sys--/reload/"> Reload.. </a>
                <br/><br/><br/>
            </body>
            """)
            return

        elif re.match(r'/?--sys--/reload/?$', path):
            referer = goto = self.headers['referer']
            if referer:
                if re.match(r'/?--sys--/reload/?$', referer):
                    goto = '/--sys--/'
            else:
                goto = '/--sys--/'

            print("Reloading...")
            self.signal_reload()  # sync reload
            print("Reloaded!")
            self.send_response(302, message="Redirect")
            self.send_header('Location', goto)
            self.end_headers()
            return

        path = unquote(path)

        curl = ContentUrl(cfg, path)

        cont = self.server.synamic_config.get_content_by_content_url(curl)
        if cont is None:
            # content urls are coditionally slashed, let's try other way
            slug = path
            if not re.match(r'.*\.[a-z0-9]+$', slug, re.I):
                if not slug.endswith('/'):
                    slug += '/'
            curl = ContentUrl(cfg, slug)
            cont = self.server.synamic_config.get_content_by_content_url(curl)
        if cont is not None:
            self.send_response(200, message="OK")
            self.end_headers()
            stream = cont.get_stream()
            while True:
                byts = stream.read(60*1024)
                if not byts:
                    break
                else:
                    self.wfile.write(byts)
            stream.close()
        else:
            self.send_response(404, message="Not FounD")
            self.end_headers()
            self.wfile.write(('Not found %s' % self.path).encode('utf-8'))

    def log_request(self, code='-', size='-'):
        print("LOG REQUEST: %s - %s - %s" % (self.path, code, size))

    def signal_stop(self):
        self.server.signaled_stop = True

    def signal_reload(self):
        self.server.signaled_reload = True
        self.server.synamic_config._reload()


class SynamicServer(http.server.HTTPServer):
    def __init__(self, config, *args, **kwargs):
        self.synamic_config = config
        self.signaled_reload = False
        self.signaled_stop = False
        super().__init__(*args, **kwargs)


def serve(config, port):
    server = SynamicServer(config, ('localhost', port), SynamicDevServerRequestHandler)
    _addr = server.server_address[0] + ":" + str(server.server_address[1])
    print("SERVE(): Server starting on %s" % _addr)
    while True:
        # server.serve_forever()
        server.handle_request()

        if server.signaled_stop:
            break
