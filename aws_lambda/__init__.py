"""
AWS Lambda handler.
Image endpoint - retrieves and decrypts image by its s3 bucket key.
"""

# make handler visible to lambda
from .handler import get_image
