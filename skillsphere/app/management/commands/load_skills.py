from django.core.management.base import BaseCommand
from app.models import Skill

class Command(BaseCommand):
    help = "Loads default skills into the database if they don't exist already."

    def handle(self, *args, **kwargs):
        default_skills = [
            ("Python", "Programming"),
            ("HTML", "Web Development"),
            ("CSS", "Web Design"),
            ("JavaScript", "Frontend"),
            ("Django", "Backend Framework"),
            ("SQL", "Database"),
            ("React", "Frontend Framework"),
            ("Git", "Version Control"),
            ("Bootstrap", "UI Framework"),
            ("Cloud Computing", "DevOps")
        ]

        added = 0
        for name, category in default_skills:
            skill, created = Skill.objects.get_or_create(name=name, category=category)
            if created:
                added += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {added} new skills added successfully!"))
