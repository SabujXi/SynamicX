import http.server


class SynamicDevServerRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        paths = self.path.split("?")
        if len(paths) > 1:
            path = "".join(paths[:-1])
            print("self.path %s and path %s" % (self.path, path))
        else:
            path = self.path

        if path == '/':
            path = '/index.html'

        url = self.server.synamic_config.get_url_by_path(path)
        if not url:
            url = self.server.synamic_config.get_url_by_path(path + "/index.html")
        if url:
            self.send_response(200, message="OK")
            self.end_headers()
            stream = url.content.get_stream()
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


class SynamicServer(http.server.HTTPServer):
    def __init__(self, config, *args, **kwargs):
        self.synamic_config = config
        super().__init__(*args, **kwargs)


def serve(config, port):
    server = SynamicServer(config, ('localhost', port), SynamicDevServerRequestHandler)
    _addr = server.server_address[0] + ":" + str(server.server_address[1])
    print("SERVE(): Server starting on %s" % _addr)
    server.serve_forever()