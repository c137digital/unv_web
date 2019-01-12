from unv.web.helpers import url_with_domain


def test_url_with_domain():
    assert url_with_domain('/path') == 'https://app.local/path'
