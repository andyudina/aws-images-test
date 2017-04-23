"""
Stores business logic of pgp keys and safe images manipulation
"""

from aws_test import settings
from aws_test.utils import download_data_from_s3, \
    decrypt_with_kms, \
    construct_private_key_from_str, \
    decrypt_with_pgp


class SafeImage:
    """
    Incapsulates image related business logic
    Retrieves and decrypts image by s3 bucket key
    """

    DEFAULT_CONTENT_TYPE = 'image/jpeg'

    def __init__(self, bucket):
        assert(bucket,
               'Bucket should not be none')
        self._bucket = bucket
        self._pgp_key = PGPKey()

    def retrieve(self):
        """
        Load and decrypt image from bucket
        """
        encrypted_image = self._load_image_from_s3()
        return self._pgp_key.decrypt_data(encrypted_image)

    def _load_image_from_s3(self):
        """
        Wrapper on s3 download api
        """
        return download_data_from_s3(
            settings.IMAGE_BUCKET, self._bucket)


class PGPKey:
    """
    Incapsulates pgp key related business logic
    """

    def decrypt_data(self, data):
        ecrypted_private_key = self._load_key_from_s3()
        private_key_str = decrypt_with_kms(ecrypted_private_key)
        private_key = construct_private_key_from_str(private_key_str)
        return decrypt_with_pgp(data, private_key)

    def _load_key_from_s3(self):
        """
        Load encrypted key from predefined s3 bucket
        """
        return download_data_from_s3(
            settings.PGP_KEY_BUCKET, settings.PGP_S3_KEY)
