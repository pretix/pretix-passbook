from django.apps import AppConfig
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy
from . import __version__
        compatibility = "pretix>=4.0.0"


class PassbookApp(AppConfig):
    name = 'pretix_passbook'
    verbose_name = 'Passbook Tickets'

    class PretixPluginMeta:
        name = gettext_lazy('Passbook Tickets')
        author = 'Tobias Kunze, Raphael Michel'
        description = gettext_lazy('Provides passbook tickets for pretix')
        category = 'FORMAT'
        visible = True
        featured = True
        version = __version__
        compatibility = "pretix>=4.0.0"

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


