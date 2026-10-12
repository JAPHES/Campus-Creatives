from django.test import TestCase
from django.urls import reverse


class PublicPageSmokeTests(TestCase):
    def test_public_index_pages_render(self):
        for route in ("core:landing", "ideas:list", "creatives:list", "showcase:list", "accounts:login", "accounts:register"):
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

    def test_directory_pages_use_the_shared_centered_hero(self):
        for route, heading_id in (
            ("ideas:list", "ideas-heading"),
            ("creatives:list", "creatives-heading"),
            ("showcase:list", "showcase-heading"),
        ):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, 'class="directory-hero"')
                self.assertContains(response, f'id="{heading_id}" class="directory-hero__title display-face"')
                self.assertNotContains(response, "-mt-8")
