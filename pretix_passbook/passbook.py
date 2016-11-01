import tempfile
from collections import OrderedDict
from typing import Tuple

from django import forms
from django.core.files.storage import default_storage
from django.utils.translation import ugettext, ugettext_lazy as _
from pretix.base.models import Order
from pretix.base.ticketoutput import BaseTicketOutput
from wallet.models import Barcode, BarcodeFormat, EventTicket, Location, Pass

from .forms import PNGImageField


class PassbookOutput(BaseTicketOutput):
    identifier = 'passbook'
    verbose_name = 'Passbook Tickets'
    download_button_icon = 'fa-mobile'
    download_button_text = _('Wallet/Passbook')

    @property
    def settings_form_fields(self) -> dict:
        return OrderedDict(
            list(super().settings_form_fields.items()) + [
                ('icon',
                 PNGImageField(
                     label=_('Event icon'),
                     required=True,
                 )),
                ('logo',
                 PNGImageField(
                     label=_('Event logo'),
                     required=True,
                 )),
                ('background',
                 PNGImageField(
                     label=_('Pass background image'),
                     required=False,
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

    def generate(self, order_position: Order) -> Tuple[str, str, str]:
        order = order_position.order
        card = EventTicket()
        card.addPrimaryField('eventName', str(order.event.name), ugettext('Event'))
        card.addPrimaryField('name', order.email, ugettext('Name'))
        if order.event.settings.show_times:
            card.addPrimaryField('doorsOpen', order.event.date_from.isoformat(), ugettext('From'))
        else:
            card.addPrimaryField('doorsOpen', order.event.date_from.date().isoformat(), ugettext('From'))
        if order.event.settings.show_date_to:
            if order.event.settings.show_times:
                card.addPrimaryField('doorsClose', order.event.date_from.isoformat(), ugettext('To'))
            else:
                card.addPrimaryField('doorsClose', order.event.date_from.date().isoformat(), ugettext('To'))

        passfile = Pass(
            card,
            passTypeIdentifier=order.event.settings.passbook_pass_type_id,
            organizationName=order.event.settings.passbook_organizer_name,
            teamIdentifier=order.event.settings.passbook_team_id,
        )

        passfile.serialNumber = '%s-%s-%s-%d' % (order.event.organizer.slug, order.event.slug, order.code,
                                                 order_position.pk)
        passfile.description = ugettext('Ticket for {}').format(order.event.name)
        passfile.barcode = Barcode(message=order_position.secret, format=BarcodeFormat.QR)
        passfile.barcode.altText = order_position.secret
        passfile.logoText = str(order.event.name)
        passfile.relevantDate = order.event.date_from.isoformat()

        if self.event.settings.passbook_latitude and self.event.settings.passbook_longitude:
            passfile.locations = Location(self.event.settings.passbook_latitude, self.event.settings.passbook_longitude)

        icon_file = self.event.settings.get('ticketoutput_passbook_icon')
        if icon_file:
            passfile.addFile('icon.png', default_storage.open(icon_file.name, 'rb'))

        logo_file = self.event.settings.get('ticketoutput_passbook_logo')
        if logo_file:
            passfile.addFile('logo.png', default_storage.open(logo_file.name, 'rb'))

        bg_file = self.event.settings.get('ticketoutput_passbook_background')
        if bg_file:
            passfile.addFile('background.png', default_storage.open(bg_file.name, 'rb'))

        filename = '{}-{}.pkpass'.format(order.event.slug, order.code)

        with tempfile.NamedTemporaryFile('w', encoding='utf-8') as keyfile:
            keyfile.write(order.event.settings.passbook_key)
            keyfile.flush()
            _pass = passfile.create(
                order.event.settings.passbook_certificate_file.name,
                keyfile.name,
                order.event.settings.passbook_wwdr_certificate_file.name,
                order.event.settings.get('passbook_key_password', '')
            )

        _pass.seek(0)
        return filename, 'application/vnd.apple.pkpass', _pass.read()
