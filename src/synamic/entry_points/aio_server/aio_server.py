from aiohttp import web
_synamic = None

async def synamic_handler(request):
    path_qs = request.path_qs
    content = _synamic.object_manager.router.get(path_qs)
    if content is None:
        return 404
    if content is static_file:
        web.FileResponse()
    elif content is dynamic_content:
        pass
    elif content is paginated_content:
        pass

app = web.Application()
app.router.add_route('GET', '/{tail:.*}', synamic_handler)


def serve(synamic):
    global _synamic
    web.run_app(app)


