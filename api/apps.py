from django.apps import AppConfig
from django.db.models.signals import post_migrate

def callback(sender, **kwargs):
    # Need local imports to wait for django apps to finish loading
    from api.populate_db import populate
    populate()

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # Hook to run scripts when app starts
    def ready(self) -> None:
        # Runs when migration is done
        post_migrate.connect(callback, dispatch_uid="app_start")

