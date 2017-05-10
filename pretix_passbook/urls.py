from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/passbookoutput/geocode/$',
        views.GeoCodeView.as_view(),
        name='geocode'),
]
