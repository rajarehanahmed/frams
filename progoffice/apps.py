from django.apps import AppConfig


class ProgofficeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'progoffice'

    def ready(self):
        from . import signals
