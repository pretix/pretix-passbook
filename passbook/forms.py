import logging
import subprocess

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def validate_rsa_privkey(value: str):
    value = value.strip()
    if not value:
        return
    if not value.startswith('-----BEGIN RSA PRIVATE KEY-----') or not value.endswith('-----END RSA PRIVATE KEY-----'):
        raise ValidationError(
            _('This does not look like a RSA private key in PEM format (it misses the begin or end signifiers)'),
        )


class CertificateFileField(forms.FileField):

    def clean(self, value, *args, **kwargs):
        value = super().clean(value, *args, **kwargs)
        if isinstance(value, UploadedFile):
            value.open('rb')
            value.seek(0)
            content = value.read()
            if content.startswith(b'-----BEGIN CERTIFICATE-----') and b'-----BEGIN CERTIFICATE-----' in content:
                return SimpleUploadedFile('cert.pem', content, 'text/plain')

            openssl_cmd = [
                'openssl',
                'x509',
                '-inform',
                'DER',
                '-outform',
                'PEM',
            ]
            process = subprocess.Popen(
                openssl_cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            process.stdin.write(content)
            pem, error = process.communicate()
            if process.returncode != 0:
                logger.info('Trying to convert a DER to PEM failed: {}'.format(error))
                raise ValidationError(
                    _('This does not look like a X509 certificate in either PEM or DER format'),
                )

            return SimpleUploadedFile('cert.pem', pem, 'text/plain')
        return value
