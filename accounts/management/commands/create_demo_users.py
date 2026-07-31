from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):

    help = "Create demo users"

    def handle(self, *args, **kwargs):

        users = [
            {
                "username": "admin",
                "email": "admin@lakchogo.com",
                "password": "Admin@123"
            },
            {
                "username": "secretary",
                "email": "secretary@lakchogo.com",
                "password": "Secretary@123"
            },
            {
                "username": "treasurer",
                "email": "treasurer@lakchogo.com",
                "password": "Treasurer@123"
            },
            {
                "username": "member",
                "email": "member@lakchogo.com",
                "password": "Member@123"
            },
        ]


        for data in users:

            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"]
                }
            )

            if created:

                user.set_password(data["password"])
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created user: {user.username}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"User already exists: {user.username}"
                    )
                )
