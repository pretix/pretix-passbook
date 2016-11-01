from collections import OrderedDict

from django import forms
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from pretix.base.signals import (
    register_global_settings, register_ticket_outputs,
)


@receiver(register_ticket_outputs, dispatch_uid='output_passbook')
def register_ticket_output(sender, **kwargs):
    from .passbook import PassbookOutput
    return PassbookOutput


@receiver(register_global_settings, dispatch_uid='passbook_settings')
def register_global_settings(sender, **kwargs):
    return OrderedDict([
        ('passbook_team_id', forms.CharField(
            label=_('Passbook team ID'),
            required=False,
        )),
        ('passbook_pass_type_id', forms.CharField(
            label=_('Passbook type'),
            required=False,
        )),
        ('passbook_organizer_name', forms.CharField(
            label=_('Passbook organizer name'),
            required=False,
        )),
        ('passbook_certificate_file', forms.FileField(required=False)),
        ('passbook_key_file', forms.FileField(required=False)),
        ('passbook_wwdr_certificate_file', forms.FileField(required=False)),
    ])
