"""
ASGI config for LakChogo Connect project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')

# Application object for ASGI servers (Daphne, Uvicorn, etc.)
application = get_asgi_application()

# For WebSocket support (if using channels):
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# 
# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter([
#             # WebSocket URL patterns
#         ])
#     ),
# })
