import tempfile
from collections import OrderedDict

from django.template.loader import get_template
from typing import Tuple

import pytz
from django import forms
from django.core.files.storage import default_storage
from django.utils.translation import ugettext, ugettext_lazy as _
from pretix.base.models import Order
from pretix.base.ticketoutput import BaseTicketOutput
from pretix.multidomain.urlreverse import build_absolute_uri
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
                     help_text=_('Display size is 29 x 29 pixels. We suggest an upload size of 87 x 87 pixels to '
                                 'support retina displays.'),
                     required=True,
                 )),
                ('logo',
                 PNGImageField(
                     label=_('Event logo'),
                     help_text=_('Display size is 160 x 50 pixels. We suggest an upload size of 480 x 150 pixels to '
                                 'support retina displays.'),
                     required=True,
                 )),
                ('background',
                 PNGImageField(
                     label=_('Pass background image'),
                     help_text=_('Display size is 180 x 220 pixels. We suggest an upload size of 540 x 660 pixels to '
                                 'support retina displays.'),
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
        tz = pytz.timezone(order.event.settings.timezone)

        card = EventTicket()

        card.addPrimaryField('eventName', str(order.event.name), ugettext('Event'))

        ticket = str(order_position.item)
        if order_position.variation:
            ticket += ' - ' + str(order_position.variation)
        card.addSecondaryField('ticket', ticket, ugettext('Product'))

        if order_position.attendee_name:
            card.addBackField('name', order_position.attendee_name, ugettext('Attendee name'))

        card.addBackField('email', order.email, ugettext('Ordered by'))
        card.addBackField('organizer', str(order.event.organizer), ugettext('Organizer'))
        if order.event.settings.contact_mail:
            card.addBackField('organizerContact', order.event.settings.contact_mail, ugettext('Organizer contact'))
        card.addBackField('orderCode', order.code, ugettext('Order code'))

        card.addAuxiliaryField('doorsOpen', order.event.get_date_from_display(tz), ugettext('From'))
        if order.event.settings.show_date_to:
            card.addAuxiliaryField('doorsClose', order.event.get_date_to_display(tz), ugettext('To'))

        card.addBackField('website', build_absolute_uri(order.event, 'presale:event.index'), ugettext('Website'))

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
        passfile.relevantDate = order.event.date_from.astimezone(tz).isoformat()

        if self.event.settings.passbook_latitude and self.event.settings.passbook_longitude:
            passfile.locations = Location(self.event.settings.passbook_latitude, self.event.settings.passbook_longitude)

        icon_file = self.event.settings.get('ticketoutput_passbook_icon')
        passfile.addFile('icon.png', default_storage.open(icon_file.name, 'rb'))

        logo_file = self.event.settings.get('ticketoutput_passbook_logo')
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

    def settings_content_render(self, request) -> str:
        if self.event.settings.get('passbook_gmaps_api_key') and self.event.location:
            template = get_template('pretix_passbook/form.html')
            return template.render({
                'request': request
            })
