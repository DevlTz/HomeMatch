from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.properties"
    label = "properties"

    def ready(self):
        # Register signal handlers (e.g. delete_fatherless_room on post_delete).
        import apps.properties.signals  # noqa: F401
