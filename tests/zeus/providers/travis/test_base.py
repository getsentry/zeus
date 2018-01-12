import pytest

from jsonschema import ValidationError

from zeus.providers.travis import TravisProvider


def test_domain_accepts_no_domain():
    data = {}
    provider = TravisProvider()
    provider.validate_config(data)
    assert data['domain'] == 'api.travis-ci.org'


def test_domain_accepts_travis_org():
    provider = TravisProvider()
    provider.validate_config({'domain': 'api.travis-ci.org'})


def test_domain_accepts_travis_com():
    provider = TravisProvider()
    provider.validate_config({'domain': 'api.travis-ci.com'})


def test_domain_rejects_random_domain():
    provider = TravisProvider()
    with pytest.raises(ValidationError):
        provider.validate_config({'domain': 'example.com'})
