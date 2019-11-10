import tempfile
from collections import OrderedDict
from typing import Tuple

import pytz
from django import forms
from django.contrib.staticfiles import finders
from django.core.files.storage import default_storage
from django.utils.formats import date_format
from django.utils.translation import ugettext, ugettext_lazy as _  # NOQA
from pretix.base.models import OrderPosition
from pretix.base.ticketoutput import BaseTicketOutput
from pretix.control.forms import ClearableBasenameFileInput
from pretix.multidomain.urlreverse import build_absolute_uri
from wallet.models import Barcode, BarcodeFormat, EventTicket, Location, Pass

from .forms import PNGImageField


class PassbookOutput(BaseTicketOutput):
    identifier = 'passbook'
    verbose_name = 'Passbook Tickets'
    download_button_icon = 'fa-mobile'
    download_button_text = _('Wallet/Passbook')
    multi_download_enabled = False

    @property
    def settings_form_fields(self) -> dict:
        return OrderedDict(
            list(super().settings_form_fields.items()) + [
                ('selfscale',
                 forms.BooleanField(
                     label=_('I would like to scale the graphics myself'),
                     help_text=_('In some instances, the downscaling of graphics done by the Wallet-app is not '
                                 'satisfactory. By checking this box, you can provide prescaled files in the correct '
                                 'dimensions.'
                                 '<br><br>'
                                 'If you choose to do so, please only upload your pictures in the regular display size '
                                 'and not the increased retina size.'),
                     required=False
                 )),
                ('icon',
                 PNGImageField(
                     label=_('Event icon'),
                     help_text='%s %s' % (
                         _('Display size is {} x {} pixels.').format(29, 29),
                         _('We suggest an upload size of {} x {} pixels to support retina displays.').format(87, 87)
                     ),
                     required=False,
                 )),
                ('icon2x',
                 PNGImageField(
                     label=_('Event icon for Retina {}x displays').format(2),
                     help_text=_('Display size is {} x {} pixels.').format(58, 58),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('icon3x',
                 PNGImageField(
                     label=_('Event icon for Retina {}x displays').format(3),
                     help_text=_('Display size is {} x {} pixels.').format(87, 87),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('logo',
                 PNGImageField(
                     label=_('Event logo'),
                     help_text='%s %s' % (
                         _('Display size is {} x {} pixels.').format(160, 50),
                         _('We suggest an upload size of {} x {} pixels to support retina displays.').format(480, 150)
                     ),
                     required=False,
                 )),
                ('logo2x',
                 PNGImageField(
                     label=_('Event logo for Retina {}x displays').format(2),
                     help_text=_('Display size is {} x {} pixels.').format(320, 100),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('logo3x',
                 PNGImageField(
                     label=_('Event logo for Retina {}x displays').format(3),
                     help_text=_('Display size is {} x {} pixels.').format(480, 150),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('background',
                 PNGImageField(
                     label=_('Pass background image'),
                     help_text='%s %s' % (
                         _('Display size is {} x {} pixels.').format(180, 220),
                         _('We suggest an upload size of {} x {} pixels to support retina displays.').format(540, 660)
                     ),
                     required=False,
                 )),
                ('background2x',
                 PNGImageField(
                     label=_('Pass background image for Retina {}x displays').format(2),
                     help_text=_('Display size is {} x {} pixels.').format(360, 440),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('background3x',
                 PNGImageField(
                     label=_('Pass background image for Retina {}x displays').format(3),
                     help_text=_('Display size is {} x {} pixels.').format(540, 660),
                     widget=ClearableBasenameFileInput(
                         attrs={
                             'data-display-dependency': '#id_ticketoutput_passbook_selfscale',
                         }
                     ),
                     required=False,
                 )),
                ('latitude',
                 forms.FloatField(
                     label=_('Event location (latitude)'),
                     help_text=_('Will be taken from event settings by default.'),
                     required=False
                 )),
                ('longitude',
                 forms.FloatField(
                     label=_('Event location (longitude)'),
                     help_text=_('Will be taken from event settings by default.'),
                     required=False
                 )),
            ]
        )

    def generate(self, order_position: OrderPosition) -> Tuple[str, str, str]:
        order = order_position.order
        ev = order_position.subevent or order.event
        tz = pytz.timezone(order.event.settings.timezone)

        card = EventTicket()

        card.addPrimaryField('eventName', str(ev.name), ugettext('Event'))

        ticket = str(order_position.item.name)
        if order_position.variation:
            ticket += ' - ' + str(order_position.variation)

        card.addSecondaryField('ticket', ticket, ugettext('Product'))
        if ev.seating_plan_id is not None:
            if order_position.seat:
                card.addAuxiliaryField('seat', str(order_position.seat), ugettext('Seat'))
            else:
                card.addAuxiliaryField('seat', ugettext('General admission'), ugettext('Seat'))

        if ev.date_admission:
            card.addBackField(
                'doorsAdmission',
                date_format(ev.date_admission.astimezone(tz), 'SHORT_DATETIME_FORMAT'),
                ugettext('Admission time')
            )

        card.addAuxiliaryField('doorsOpen', ev.get_date_from_display(tz, short=True), ugettext('From'))
        if order.event.settings.show_date_to and ev.date_to:
            if ev.seating_plan_id:
                card.addBackField('doorsClose', ev.get_date_to_display(tz, short=True), ugettext('To'))
            else:
                card.addAuxiliaryField('doorsClose', ev.get_date_to_display(tz, short=True), ugettext('To'))

        if order_position.attendee_name:
            card.addBackField('name', order_position.attendee_name, ugettext('Attendee name'))

        card.addBackField('email', order.email, ugettext('Ordered by'))
        card.addBackField('organizer', str(order.event.organizer), ugettext('Organizer'))
        if order.event.settings.contact_mail:
            card.addBackField('organizerContact', order.event.settings.contact_mail, ugettext('Organizer contact'))
        card.addBackField('orderCode', order.code, ugettext('Order code'))

        if order_position.subevent:
            card.addBackField('website', build_absolute_uri(order.event, 'presale:event.index', {
                'subevent': order_position.subevent.pk
            }), ugettext('Website'))
        else:
            card.addBackField('website', build_absolute_uri(order.event, 'presale:event.index'), ugettext('Website'))

        passfile = Pass(
            card,
            passTypeIdentifier=order.event.settings.passbook_pass_type_id,
            organizationName=order.event.settings.passbook_organizer_name,
            teamIdentifier=order.event.settings.passbook_team_id,
        )

        passfile.serialNumber = '%s-%s-%s-%d' % (order.event.organizer.slug, order.event.slug, order.code,
                                                 order_position.pk)

        passfile.description = ugettext('Ticket for {event} ({product})').format(event=ev.name, product=ticket)
        passfile.barcode = Barcode(message=order_position.secret, format=BarcodeFormat.QR)
        passfile.barcode.altText = order_position.secret
        passfile.relevantDate = ev.date_from.astimezone(tz).isoformat()

        if self.event.settings.passbook_latitude and self.event.settings.passbook_longitude:
            passfile.locations = [Location(self.event.settings.passbook_latitude,
                                           self.event.settings.passbook_longitude)]
        elif order_position.subevent and order_position.subevent.geo_lat and order_position.subevent.geo_lon:
            passfile.locations = [Location(order_position.subevent.geo_lat, order_position.subevent.geo_lon)]
        elif self.event.geo_lat and self.event.geo_lon:
            passfile.locations = [Location(self.event.geo_lat, self.event.geo_lon)]

        icon_file = self.event.settings.get('ticketoutput_passbook_icon')
        if icon_file:
            passfile.addFile('icon.png', default_storage.open(icon_file.name, 'rb'))
        else:
            passfile.addFile('icon.png', open(finders.find('pretix_passbook/icon.png'), "rb"))

        logo_file = self.event.settings.get('ticketoutput_passbook_logo')
        if logo_file:
            passfile.addFile('logo.png', default_storage.open(logo_file.name, 'rb'))
        else:
            passfile.logoText = str(ev.name)
            passfile.addFile('logo.png', open(finders.find('pretix_passbook/logo.png'), "rb"))

        bg_file = self.event.settings.get('ticketoutput_passbook_background')
        if bg_file:
            passfile.addFile('background.png', default_storage.open(bg_file.name, 'rb'))

        if self.event.settings.get('ticketoutput_passbook_selfscale'):
            icon2x_file = self.event.settings.get('ticketoutput_passbook_icon2x')
            if icon2x_file:
                passfile.addFile('icon@2x.png', default_storage.open(icon2x_file.name, 'rb'))

            icon3x_file = self.event.settings.get('ticketoutput_passbook_icon3x')
            if icon3x_file:
                passfile.addFile('icon@3x.png', default_storage.open(icon3x_file.name, 'rb'))

            logo2x_file = self.event.settings.get('ticketoutput_passbook_logo2x')
            if logo2x_file:
                passfile.addFile('logo@2x.png', default_storage.open(logo2x_file.name, 'rb'))

            logo3x_file = self.event.settings.get('ticketoutput_passbook_logo3x')
            if logo3x_file:
                passfile.addFile('logo@3x.png', default_storage.open(logo3x_file.name, 'rb'))

            bg2x_file = self.event.settings.get('ticketoutput_passbook_background2x')
            if bg2x_file:
                passfile.addFile('background2x.png', default_storage.open(bg2x_file.name, 'rb'))

            bg3x_file = self.event.settings.get('ticketoutput_passbook_background3x')
            if bg3x_file:
                passfile.addFile('background@3x.png', default_storage.open(bg3x_file.name, 'rb'))

        filename = '{}-{}.pkpass'.format(order.event.slug, order.code)

        with tempfile.NamedTemporaryFile('w', encoding='utf-8') as keyfile, \
                tempfile.NamedTemporaryFile('w', encoding='utf-8') as certfile, \
                tempfile.NamedTemporaryFile('w', encoding='utf-8') as cafile:

            certfile.write(order.event.settings.passbook_certificate_file.read())
            certfile.flush()

            cafile.write(order.event.settings.passbook_wwdr_certificate_file.read())
            cafile.flush()

            keyfile.write(order.event.settings.passbook_key)
            keyfile.flush()
            _pass = passfile.create(
                certfile.name,
                keyfile.name,
                cafile.name,
                order.event.settings.get('passbook_key_password', '')
            )

        _pass.seek(0)
        return filename, 'application/vnd.apple.pkpass', _pass.read()
