from django.apps import AppConfig
from django.utils.functional import cached_property
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

    @cached_property
    def compatibility_errors(self):
        import shutil
        errs = []
        if not shutil.which('openssl'):
            errs.append("The OpenSSL binary is not installed or not in the PATH.")
        return errs


default_app_config = 'passbook.PassbookApp'
