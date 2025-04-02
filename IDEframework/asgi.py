"""
ASGI config for IDEframework project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import group_learn.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IDEframework.settings')

# application = get_asgi_application()
django_asgi_app = get_asgi_application()

from group_learn.routing import websocket_urlpatterns

# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(
#             AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
#         ),
#     }
# )

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 请求走 Django
    "websocket": AuthMiddlewareStack(  # WebSocket 走你的路由
        URLRouter(
            group_learn.routing.websocket_urlpatterns
        )
    ),
})