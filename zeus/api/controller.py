from flask import Blueprint
from uuid import uuid4


class Controller(Blueprint):
    def add_resource(self, path, cls):
        self.add_url_rule(
            path, view_func=cls.as_view(
                name=uuid4().hex,
            )
        )
