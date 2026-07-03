from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Must match the path in INSTALLED_APPS in settings.py
    name = 'apps.accounts'
    verbose_name = 'Accounts'
