import pytest

from unv.web.core import create_app
from unv.web.app import setup as setup_app


@pytest.mark.asyncio
async def test_create_app():
    app = create_app(link_static=False)
    setup_app(app)
    assert app['jinja2']
