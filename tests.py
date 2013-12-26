"""
The following tests are integration tests that need a valid
Netflix API key and secret to run sucessfully.
"""

import os

import pytest

from netflix import NetflixAPI, NetflixAuthError

NETFLIX_API_KEY = os.environ["NETFLIX_API_KEY"]
NETFLIX_API_SECRET = os.environ["NETFLIX_API_SECRET"]


@pytest.fixture
def api():
    return NetflixAPI(
        api_key=NETFLIX_API_KEY,
        api_secret=NETFLIX_API_SECRET,
    )


def test_needs_an_valid_api_key_and_secret():
    api = NetflixAPI("fake_api_key", "fake_api_secret")

    with pytest.raises(NetflixAuthError):
        api.get("catalog/titles", {
            'term': "Shawshawk Redemption",
            'max_results': 10
        })


def test_get_authorization_url(api):
    auth_properties = api.get_authentication_tokens()

    assert "application_name" in auth_properties
    assert "auth_url" in auth_properties
    assert "login_url" in auth_properties
    assert "oauth_token" in auth_properties
    assert "oauth_token_secret" in auth_properties


def test_simple_catalog_search(api):
    response = api.get("catalog/titles", {
        'term': "Shawshawk Redemption",
        'max_results': 10
    })

    root = response["catalog_titles"]

    assert "number_of_results" in root
    assert "url_template" in root
    assert "start_index" in root
    assert "link" in root

    titles = root["catalog_title"]

    first_result = titles[0]

    assert "id" in first_result
    assert "title" in first_result
    assert "runtime" in first_result
    assert "box_art" in first_result
