from django.apps import AppConfig
from pretix.base.plugins import PluginType


class PassbookApp(AppConfig):
    name = 'passbook'
    verbose_name = 'Passbook Tickets'

    class PretixPluginMeta:
        name = 'Passbook Tickets'
        author = 'Tobias Kunze'
        description = 'Provides passbook tickets for pretix'
        visible = True
        version = '0.0'
        type = PluginType.ADMINFEATURE

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'passbook.PassbookApp'
