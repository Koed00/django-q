VERSION = (1, 3, 1)

default_app_config = "django_q.apps.DjangoQConfig"


__all__ = ["conf", "cluster", "models", "tasks", "croniter"]

# Optional Imports
try:
    from croniter import croniter
except ImportError:
    croniter = None
