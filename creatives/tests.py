from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from accounts.models import User

from .forms import CreativeProfileForm
from .models import Campus, Skill


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CreativeProfileFormTests(TestCase):
    def test_profile_limits_skills_to_three(self):
        user = User.objects.create_user(email="creative@example.com", password="pass")
        campus = Campus.objects.create(name="Test University")
        skills = [Skill.objects.create(name=f"Skill {number}") for number in range(4)]
        form = CreativeProfileForm(
            data={
                "name": "Test Creative",
                "bio": "A creative bio",
                "campus": campus.pk,
                "skills": [skill.pk for skill in skills],
                "is_available": True,
            },
            instance=user.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("no more than three", str(form.errors["skills"]))

    def test_model_relationship_also_rejects_a_fourth_skill(self):
        user = User.objects.create_user(email="limit@example.com", password="pass")
        skills = [Skill.objects.create(name=f"Direct Skill {number}") for number in range(4)]
        user.profile.skills.add(*skills[:3])
        with self.assertRaises(ValidationError):
            user.profile.skills.add(skills[3])
