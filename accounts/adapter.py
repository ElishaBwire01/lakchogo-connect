import random
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Automatically populate required fields for Google signups.
    """

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # Generate unique phone if missing
        if not getattr(user, "phone", None):
            while True:
                phone = f"+2547{random.randint(10000000,99999999)}"
                if not User.objects.filter(phone=phone).exists():
                    user.phone = phone
                    break

        # Generate unique ID number if missing
        if not getattr(user, "id_number", None):
            while True:
                id_number = f"GOOGLE{random.randint(10000000,99999999)}"
                if not User.objects.filter(id_number=id_number).exists():
                    user.id_number = id_number
                    break

        return user
