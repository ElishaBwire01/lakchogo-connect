from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'REST API'

    def ready(self):
        try:
            import api.signals
        except ImportError:
            # Signals file doesn't exist yet, skip
            pass
