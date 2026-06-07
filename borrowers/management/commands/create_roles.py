from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        roles = [
            "Manager",
            "Loan Officer",
            "Cashier",
            "Auditor"
        ]

        for role in roles:
            group, created = Group.objects.get_or_create(name=role)

            if created:
                self.stdout.write(self.style.SUCCESS(f"{role} created"))
            else:
                self.stdout.write(f"{role} already exists")