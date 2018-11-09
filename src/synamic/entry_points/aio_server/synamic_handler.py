from synamic.core.contracts import CDocType
from aiohttp import web


async def synamic_handler(request):
    synamic = request.app.synamic
    path_qs = request.path_qs
    print(f'Requesting: {path_qs}')
    # content = synamic.object_manager.router.get(path_qs)
    content = synamic.router.get_content(path_qs)
    if content is None:
        text = f"Not found for {path_qs}"
        mimetype = 'text/html'
        response = web.Response(text=text, content_type=mimetype)
    else:
        mimetype = content.mimetype
        print(f'Found content for {path_qs} as mimetype {mimetype} and cdoctype {content.cdoctype}')
        if CDocType.is_binary(content.cdoctype, not_generated=True):
            # serve static
            response = web.FileResponse(content.cpath.abs_path)
            response.content_type = mimetype

        elif CDocType.is_binary(content.cdoctype):
            # serve as stream.
            data = content.body_as_bytes
            response = web.Response(body=data, content_type=mimetype)
        else:
            # text content.
            with content.get_stream() as s:
                data = s.read()
            text = data.decode('utf-8')
            response = web.Response(text=text, content_type=mimetype)
    return response
