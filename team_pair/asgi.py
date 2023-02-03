"""
ASGI config for team_pair project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_pair.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": 
        AuthMiddlewareStack(
            URLRouter([
                re_path(r"^ws/$", consumers.Watcher.as_asgi()),
            ])
        )
})