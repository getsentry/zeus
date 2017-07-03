from zeus.testutils import TestCase

class AuthIndexResourceTest(TestCase):
    def test_anonymous(self):
        r = self.client.get('/api/0/auth/')
        assert self.from_json(r) == {'authenticated': False}