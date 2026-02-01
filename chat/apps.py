from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    def ready(self):
        # Import signals to ensure handlers are connected
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
