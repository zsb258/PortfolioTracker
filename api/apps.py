from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # Hook to run scripts when app starts
    def ready(self) -> None:
        # doing local imports as django prevents top level imports in `apps.py`
        from api.populate_db import populate

        # populate()
