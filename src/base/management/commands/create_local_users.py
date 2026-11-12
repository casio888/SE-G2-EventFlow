from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from authentication.models import (
    Address,
    CustomUserContributer,
    CustomUserOrganizer,
)


class Command(BaseCommand):
    help = "Create the local contributor and organizer accounts."

    @transaction.atomic
    def handle(self, *args, **options):
        address, _ = Address.objects.get_or_create(
            country="Germany",
            city="Dresden",
            street="EventFlow",
            houseNbr=1,
        )

        accounts = (
            (CustomUserContributer, "contrib", "contrib@local.de"),
            (CustomUserOrganizer, "event", "event@local.de"),
        )
        for user_model, username, email in accounts:
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"Already exists {email}")
                continue

            user_model.objects.create_user(
                username=username,
                email=email,
                password="aaaaaaaa123",
                address=address,
                telephone="+49123456789",
            )

            self.stdout.write(f"Created {email}")
