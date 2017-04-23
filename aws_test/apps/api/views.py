"""
API endpoints to fire on lambda
"""

from django.http import HttpResponse

from .models import SafeImage


def get_image_view(request, image_bucket):
    """
    API endpoint for serving image
    """
    image = SafeImage(bucket=image_bucket).retrieve()
    return HttpResponse(
        image, content_type=SafeImage.DEFAULT_CONTENT_TYPE)
