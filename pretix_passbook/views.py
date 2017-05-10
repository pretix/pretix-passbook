import logging

from django.http import JsonResponse
from django.views import View
from googlemaps import Client
from googlemaps.exceptions import ApiError

from pretix.control.permissions import EventPermissionRequiredMixin

logger = logging.getLogger(__name__)


class GeoCodeView(EventPermissionRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        c = Client(key=request.event.settings.get('passbook_gmaps_api_key'))
        try:
            r = c.geocode(address=request.event.location, language=request.LANGUAGE_CODE.split("_")[0])
        except ApiError:
            logger.exception('Google Maps API Error')
            return JsonResponse({
                'status': 'error',
            })
        else:
            return JsonResponse({
                'status': 'ok',
                'result': r
            })
