from unv.web.helpers import url_with_domain, url_for_static


def test_url_with_domain():
    assert url_with_domain('/path') == 'https://app.local/path'


def test_simple_static_url():
    assert url_for_static('asd.txt') == '/static/asd.txt'
