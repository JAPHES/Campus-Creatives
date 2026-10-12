from django.contrib.auth import get_user_model
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

    def test_shared_layout_uses_the_responsive_sidebar(self):
        response = self.client.get(reverse("core:landing"))

        self.assertContains(response, 'id="app-sidebar"')
        self.assertContains(response, "data-sidebar-toggle")
        self.assertContains(response, reverse("ideas:list"))
        self.assertContains(response, reverse("creatives:list"))
        self.assertContains(response, reverse("showcase:list"))
        self.assertNotContains(response, "data-mobile-menu")

    def test_authenticated_navigation_is_in_the_sidebar(self):
        user = get_user_model().objects.create_user(email="creative@example.com", password="test-password")
        self.client.force_login(user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertContains(response, ">Dashboard</span>")
        self.assertContains(response, ">My projects</span>")
        self.assertContains(response, ">Post an idea</span>")
        self.assertContains(response, ">Settings</span>")
        self.assertContains(response, 'action="{}"'.format(reverse("accounts:logout")))
