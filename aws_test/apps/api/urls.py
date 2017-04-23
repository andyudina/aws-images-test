from django.conf.urls import url

from .views import get_image_view


urlpatterns = [
    url(r'^(?P<image_bucket>[\w\-]+)',
        get_image_view,
        name='get-image')
]
