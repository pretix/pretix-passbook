from collections import OrderedDict
from typing import Tuple

from django import forms
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _
from pretix.base.models import Order
from pretix.base.ticketoutput import BaseTicketOutput
from wallet.models import Barcode, BarcodeFormat, EventTicket, Location, Pass


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

    def generate(self, order: Order) -> Tuple[str, str, str]:
        card = EventTicket()
        card.addPrimaryField('event', str(order.event.name), 'Event')
        card.addPrimaryField('name', order.email, 'Name')

        passfile = Pass(
            card,
            passTypeIdentifier=order.event.settings.passbook_type_id,
            organizationName=order.event.settings.passbook_organizer_name,
            teamIdentifier=order.event.settings.passbook_team_id,
        )

        passfile.serialNumber = order.code
        passfile.description = str(_('Ticket for {}').format(order.event.name))
        passfile.barcode = Barcode(message=order.secret, format=BarcodeFormat.QR)
        passfile.logoText = str(order.event.name)
        passfile.userInfo = order.email

        if self.event.settings.passbook_latitude and self.event.settings.passbook_longitude:
            passfile.locations = Location(self.event.settings.passbook_latitude, self.event.settings.passbook_longitude)

        icon_file = self.event.settings.get('ticketoutput_passbook_icon')
        logo_file = self.event.settings.get('ticketoutput_passbook_logo')
        passfile.addFile('icon.png', default_storage.open(icon_file.name, 'rb'))
        passfile.addFile('logo.png', default_storage.open(logo_file.name, 'rb'))

        filename = '{}-{}.pkpass'.format(order.event.slug, order.code)
        _pass = passfile.create(
            order.event.settings.passbook_certificate_file.name,
            order.event.settings.passbook_key_file.name,
            order.event.settings.passbook_wwdr_certificate_file.name,
            filename, '',
        )
        _pass.seek(0)
        return filename, 'application/vnd.apple.pkpass', _pass.read()
