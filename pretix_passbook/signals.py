from collections import OrderedDict
from django import forms
from django.core.files import File
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import register_global_settings, register_ticket_outputs

from .forms import CertificateFileField, validate_rsa_privkey


@receiver(register_ticket_outputs, dispatch_uid="output_passbook")
def register_ticket_output(sender, **kwargs):
    from .passbook import PassbookOutput

    return PassbookOutput


@receiver(register_global_settings, dispatch_uid="passbook_settings")
def register_global_settings(sender, **kwargs):
    return OrderedDict(
        [
            (
                "passbook_team_id",
                forms.CharField(
                    label=_("Passbook: Team ID"),
                    help_text=_(
                        "The Team ID can be found under 'Organizational Unit' when "
                        "opening the certificate, e.g. with Keychain on MacOS or you "
                        "can find it in your Apple developer account"
                    ),
                    required=False,
                ),
            ),
            (
                "passbook_pass_type_id",
                forms.CharField(
                    label=_("Passbook: Pass Type ID"),
                    help_text=_(
                        "The Pass Type ID is your identifier, for example pass.pretix.example"
                    ),
                    required=False,
                ),
            ),
            (
                "passbook_certificate_file",
                CertificateFileField(
                    label=_("Passbook: Pass Type ID Certificate"),
                    required=False,
                ),
            ),
            (
                "passbook_wwdr_certificate_file",
                CertificateFileField(
                    label=_("Passbook: Apple Intermediate Certificate"),
                    help_text=_(
                        "You can download the current certificate from Apple at "
                        "https://www.apple.com/certificateauthority/AppleWWDRCAG4.cer"
                    ),
                    required=False,
                ),
            ),
            (
                "passbook_key",
                forms.CharField(
                    label=_("Passbook: RSA private key"),
                    required=False,
                    widget=forms.Textarea,
                    validators=[validate_rsa_privkey],
                ),
            ),
            (
                "passbook_key_password",
                forms.CharField(
                    label=_("Passbook: RSA private key password"),
                    widget=forms.PasswordInput(render_value=True),
                    required=False,
                    help_text=_(
                        "Optional, only necessary if the RSA private key entered above requires a password."
                    ),
                ),
            ),
        ]
    )


settings_hierarkey.add_default("passbook_certificate_file", None, File)
settings_hierarkey.add_default("passbook_wwdr_certificate_file", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_background", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_background2x", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_background3x", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_icon", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_icon2x", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_icon3x", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_logo", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_logo2x", None, File)
settings_hierarkey.add_default("ticketoutput_passbook_logo3x", None, File)
