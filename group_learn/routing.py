from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/group_learn/(?P<course_name>[^/]+)/(?P<room_name>[^/]+)/$", consumers.ChatConsumer.as_asgi()),
]