from zeus.providers.base import Provider


class CustomProvider(Provider):
    def get_config(self):
        return {"properties": {"name": {"type": "string"}}, "required": ["name"]}

    def get_name(self, config):
        return config.get("name", "custom")
