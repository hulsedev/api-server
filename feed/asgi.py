"""
ASGI config for feed project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

import django_eventstream
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            [
                # TODO: remove this channel
                re_path(
                    "events/",
                    AuthMiddlewareStack(
                        URLRouter(django_eventstream.routing.urlpatterns)
                    ),
                    {"channels": ["team"]},
                ),
                re_path(
                    r"^consumer/(?P<member_id>[^/]+)/",
                    AuthMiddlewareStack(
                        URLRouter(django_eventstream.routing.urlpatterns)
                    ),
                    {"format-channels": ["consumer-{member_id}"]},
                ),
                re_path(
                    r"^producer/(?P<member_id>[^/]+)/",
                    AuthMiddlewareStack(
                        URLRouter(django_eventstream.routing.urlpatterns)
                    ),
                    {"format-channels": ["producer-{member_id}"]},
                ),
                re_path(r"", get_asgi_application()),
            ]
        ),
    }
)
