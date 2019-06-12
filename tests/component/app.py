from aiohttp import web

from unv.web.decorators import render, as_json, with_headers


async def index(request: web.Request):
    return web.Response(body='index')


@render('page.html')
async def page(request: web.Request):
    return {'value': 2}


@with_headers({
    'Accept-Some': '1'
})
@as_json
async def json(request: web.Request):
    return {'value': 2}


def setup(app: web.Application):
    app.router.add_get('/', index)
    app.router.add_get('/page', page)
    app.router.add_get('/json', json)
