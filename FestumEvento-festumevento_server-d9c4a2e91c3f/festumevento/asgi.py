import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from api import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'festumevento.settings')
django.setup()

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  # Just HTTP for now. (We can add other protocols later.)
  "websocket": AuthMiddlewareStack(
    URLRouter(
      routing.websocket_urlpatterns
    )
  )
})