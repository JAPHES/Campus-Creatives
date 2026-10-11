from django.core.management.base import BaseCommand

from creatives.models import Campus, Skill


CAMPUSES = [
    ("University of Lagos", "Lagos", "Lagos"),
    ("University of Ibadan", "Ibadan", "Oyo"),
    ("University of Nigeria, Nsukka", "Nsukka", "Enugu"),
    ("Obafemi Awolowo University", "Ile-Ife", "Osun"),
    ("Ahmadu Bello University", "Zaria", "Kaduna"),
    ("University of Benin", "Benin City", "Edo"),
    ("University of Abuja", "Abuja", "FCT"),
    ("Covenant University", "Ota", "Ogun"),
]

SKILLS = [
    ("Brand design", "Design"),
    ("UI/UX design", "Design"),
    ("Illustration", "Design"),
    ("Photography", "Visual media"),
    ("Videography", "Visual media"),
    ("Video editing", "Visual media"),
    ("Motion design", "Visual media"),
    ("Writing", "Storytelling"),
    ("Copywriting", "Storytelling"),
    ("Social media", "Marketing"),
    ("Music production", "Audio"),
    ("Sound design", "Audio"),
    ("Web development", "Technology"),
    ("Product management", "Strategy"),
]


class Command(BaseCommand):
    help = "Add an editable starter catalog of campuses and creative skills."

    def handle(self, *args, **options):
        campus_count = 0
        skill_count = 0
        for name, city, state in CAMPUSES:
            _, created = Campus.objects.get_or_create(name=name, defaults={"city": city, "state": state})
            campus_count += int(created)
        for name, category in SKILLS:
            _, created = Skill.objects.get_or_create(name=name, defaults={"category": category})
            skill_count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Added {campus_count} campuses and {skill_count} skills. Existing records were preserved."))
