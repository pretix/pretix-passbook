from collections import OrderedDict
from typing import Tuple

from django import forms
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _

from pretix.base.models import Order
from pretix.base.ticketoutput import BaseTicketOutput


class PassbookOutput(BaseTicketOutput):
    identifier = 'passbook'
    verbose_name = 'Passbook Tickets'
    download_button_icon = 'mobile'
    download_button_text = _('Download passbook ticket')

    @property
    def settings_form_fields(self) -> dict:
        return OrderedDict(
            list(super().settings_form_fields.items()) + [
                ('icon',
                    forms.FileField(
                        label=_('Event icon'),
                        required=True,
                    )),
                ('logo',
                    forms.FileField(
                        label=_('Event logo (.png)'),
                        required=True,
                    )),
                ('latitude',
                    forms.FloatField(
                        label=_('Event location (latitude)'),
                        required=False
                    )),
                ('longitude',
                    forms.FloatField(
                        label=_('Event location (longitude)'),
                        required=False
                    )),
            ]
        )

    def settings_content_render(self, request: HttpRequest) -> str:
        pass

    def generate(self, order: Order) -> Tuple[str, str, str]:
        pass
