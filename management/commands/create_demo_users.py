from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):

    help = "Create demo users"

    def handle(self, *args, **kwargs):

        users = [

            {
                "username": "admin",
                "first_name": "System",
                "last_name": "Administrator",
                "email": "admin@lakchogo.com",
                "phone": "0700000001",
                "id_number": "ADMIN001",
                "password": "Admin@123",
                "is_staff": True,
                "is_superuser": True,
            },

            {
                "username": "secretary",
                "first_name": "John",
                "last_name": "Secretary",
                "email": "secretary@lakchogo.com",
                "phone": "0700000002",
                "id_number": "SECRETARY001",
                "password": "Secretary@123",
            },

            {
                "username": "treasurer",
                "first_name": "Mary",
                "last_name": "Treasurer",
                "email": "treasurer@lakchogo.com",
                "phone": "0700000003",
                "id_number": "TREASURER001",
                "password": "Treasurer@123",
            },

            {
                "username": "member",
                "first_name": "Demo",
                "last_name": "Member",
                "email": "member@lakchogo.com",
                "phone": "0700000004",
                "id_number": "MEMBER001",
                "password": "Member@123",
            },

        ]


        for data in users:

            password = data.pop("password")

            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults=data
            )

            if created:
                user.set_password(password)
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created user: {user.username}"
                    )
                )

            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {user.username}"
                    )
                )
