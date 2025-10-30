from django.apps import AppConfig

class SocialfeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialfeed'

    def ready(self):
        from . import signals  # noqa

class WebrtcLiveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webrtc_live"

