from weights.models import PigeonUser
from django.test import Client, TestCase


class StaticPagesTestCase(TestCase):
    fixtures = ['user.json', 'products.json', 'measures.json']

    def setUp(self):
        self.client = Client()
        self.client.force_login(PigeonUser.objects.get(username="test_user_1"))

    def test_about_page(self):
        resp = self.client.get("/en/about")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Fabien Bourrel", resp.content)

    def test_contribute_page(self):
        resp = self.client.get("/en/contribute")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"How to contribute", resp.content)

    def test_home_page(self):
        resp = self.client.get("/en/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"static/images/benoit.png", resp.content)
        self.assertIn(b"static/images/fabien.png", resp.content)
        self.assertIn(b"static/images/logo.png", resp.content)
