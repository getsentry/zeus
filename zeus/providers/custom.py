from zeus.providers.base import Provider


class CustomProvider(Provider):

    def get_config(self):
        return {"properties": {}, "required": []}
