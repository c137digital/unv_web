import pytest

from unv.web.core import create_app


@pytest.mark.asyncio
async def test_create_app():
    app = create_app()
    assert app['jinja2']
