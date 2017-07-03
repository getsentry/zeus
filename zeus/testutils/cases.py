import json
import unittest

from exam import Exam, fixture
from flask import current_app as app

from zeus.config import db
from zeus.models import User

from .fixtures import Fixtures


class AuthMixin(object):
    @fixture
    def default_user(self):
        user = User(
            email='foo@example.com',
        )
        db.session.add(user)
        db.session.commit()

        return user

    def login(self, user):
        with self.client.session_transaction() as session:
            session['uid'] = user.id.hex

    def login_default(self):
        return self.login(self.default_user)

    def login_default_admin(self):
        return self.login(self.default_admin)


class TestCase(Exam, unittest.TestCase, Fixtures, AuthMixin):
    def setUp(self):
        super(TestCase, self).setUp()
        self.client = app.test_client()
        # initiate a session
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        super(TestCase, self).tearDown()

    def from_json(self, response):
        assert response.headers['Content-Type'] == 'application/json'
        return json.loads(response.data)
