"""
WSGI config for LakChogo Connect project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')

# Application object for WSGI servers (Gunicorn, uWSGI, etc.)
application = get_wsgi_application()

# For production, you may want to use:
# from whitenoise import WhiteNoise
# application = WhiteNoise(application)
# application.add_files(settings.STATIC_ROOT, prefix=settings.STATIC_URL)
