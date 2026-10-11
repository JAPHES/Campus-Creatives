from django.test import TestCase
from django.urls import reverse


class PublicPageSmokeTests(TestCase):
    def test_public_index_pages_render(self):
        for route in ("core:landing", "ideas:list", "creatives:list", "showcase:list", "accounts:login", "accounts:register"):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)
