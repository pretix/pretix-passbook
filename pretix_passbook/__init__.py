from django.apps import AppConfig
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy


class PassbookApp(AppConfig):
    name = 'pretix_passbook'
    verbose_name = 'Passbook Tickets'

    class PretixPluginMeta:
        name = ugettext_lazy('Passbook Tickets')
        author = 'Tobias Kunze, Raphael Michel'
        description = ugettext_lazy('Provides passbook tickets for pretix')
        visible = True
        version = '1.6.1'

    def ready(self):
        from . import signals  # NOQA

    @cached_property
    def compatibility_errors(self):
        import shutil
        errs = []
        if not shutil.which('openssl'):
            errs.append("The OpenSSL binary is not installed or not in the PATH.")
        return errs

    @cached_property
    def compatibility_warnings(self):
        errs = []
        try:
            from PIL import Image  # NOQA
        except ImportError:
            errs.append("Pillow is not installed on this system, which is required for converting and scaling images.")
        return errs


default_app_config = 'pretix_passbook.PassbookApp'
