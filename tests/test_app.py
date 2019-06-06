import pytest

from aiohttp import web

from unv.app.base import Application
from unv.web.deploy import SETTINGS as DEPLOY_SETTINGS


async def test_simple_web_app(aiohttp_client):
    app = Application()
    web_app = app[web.Application]
    client = await aiohttp_client(web_app)
    assert web_app['jinja2']

    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert text == 'index'

    resp = await client.get('/page')
    assert resp.status == 200
    assert resp.content_type == 'text/html'
    text = await resp.text()
    assert '<h1>This is test: 2</h1>' in text

    resp = await client.get('/json')
    assert resp.status == 200
    assert resp.content_type == 'application/json'
    data = await resp.json()
    assert data['value'] == 2

    assert not DEPLOY_SETTINGS.static_link
