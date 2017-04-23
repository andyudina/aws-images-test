"""
API endpoints to fire on lambda
"""

from django.shortcuts import render

from .models import SafeImage


def get_image_view(request, image_bucket):
    """
    API endpoint for serving image
    """
    image = SaveImage(bucket=image_bucket).retrieve()
    return HttpResponse(
        image, content_type=SafeImage.DEFAULT_CONTENT_TYPE)
