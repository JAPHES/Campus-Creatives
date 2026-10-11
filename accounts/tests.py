from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class RegistrationTests(TestCase):
    def test_registration_uses_email_and_creates_named_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {"name": "Ada Creative", "email": "ada@example.com", "password1": "A-long-test-pass-984!", "password2": "A-long-test-pass-984!"},
        )
        self.assertRedirects(response, reverse("accounts:settings"))
        user = User.objects.get(email="ada@example.com")
        self.assertEqual(user.profile.name, "Ada Creative")
        self.assertTrue(user.check_password("A-long-test-pass-984!"))

    def test_profile_settings_and_admin_user_add_pages_render(self):
        user = User.objects.create_superuser(email="admin@example.com", password="test-password")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("accounts:settings")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:accounts_user_add")).status_code, 200)
