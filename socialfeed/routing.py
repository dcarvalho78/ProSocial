from django.urls import re_path
from .consumers import LiveConsumer

websocket_urlpatterns = [
    re_path(r"^ws/live/(?P<room>[\w\-]+)/$", LiveConsumer.as_asgi()),
]
