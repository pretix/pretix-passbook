from django.dispatch import receiver

from pretix.base.signals import register_ticket_outputs


@receiver(register_ticket_outputs, dispatch_uid='output_pdf')
def register_ticket_output(sender, **kwargs):
    from .passbook import PassbookOutput
    return PassbookOutput
