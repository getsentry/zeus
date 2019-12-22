from .custom import CustomProvider
from .travis import TravisProvider

ALIASES = {"travis-ci": "travis"}

PROVIDERS = {"travis": TravisProvider, "custom": CustomProvider}

VALID_PROVIDER_NAMES = tuple(set(PROVIDERS.keys()).union(ALIASES.keys()))


class InvalidProvider(Exception):
    pass


def get_provider(provider_name):
    try:
        return PROVIDERS[ALIASES.get(provider_name, provider_name)]()
    except KeyError:
        raise InvalidProvider(provider_name)
