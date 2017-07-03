from zeus.testutils import TestCase


class AuthIndexResourceTest(TestCase):
    def test_anonymous(self):
        r = self.client.get('/api/0/auth/')
        assert self.from_json(r) == {'authenticated': False}

    def test_authenticated(self):
        self.login_default()

        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = self.from_json(resp)
        assert data['authenticated'] is True
        assert data['user']['id'] == self.default_user.id.hex
