from zeus.providers.base import Provider


class TravisProvider(Provider):
    def get_config(self):
        return {
            'properties': {
                'domain': {
                    'type': 'string',
                    'enum': ['api.travis-ci.com', 'api.travis-ci.org'],
                    'default': 'api.travis-ci.org',
                },
            },
            'required': ['domain']
        }
