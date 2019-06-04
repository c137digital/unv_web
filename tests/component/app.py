from aiohttp import web

# TODO: add views with tests
# view with json render
# view with html render with jinja
from unv.web.decorators import render, as_json


async def index(request: web.Request):
    return web.Response(body='index')


@render('page.html')
async def page(request: web.Request):
    return {'value': 2}


@as_json
async def json(request: web.Request):
    return {'value': 2}


def setup(app: web.Application):
    app.router.add_get('/', index)
    app.router.add_get('/page', page)
    app.router.add_get('/json', json)
