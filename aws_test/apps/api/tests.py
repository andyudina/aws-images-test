"""
Functional tests of safe image logic.
WARNING: tests only ideal scenario (kind of smoke)
Cover exceptions with test (like bucket does not exist) before go to prod.

TODO: modules heavily depend on utils.
Cover utils with units befre go to prod
"""
import io
from unittest import TestCase, skip
from mock import patch, PropertyMock

from aws_test import settings
from aws_test.utils import \
    generate_pgp_key_pair, \
    encrypt_file_with_pgp, \
    encrypt_with_kms, \
    store_data_at_s3, \
    generate_random_string
from .models import PGPKey, SafeImage


TEST_NOT_IMPLEMENTED_WARNING = 'Sorry, not implemented yet. Please, FIXME'

# Constants for random jpegs
IMAGE_HEIGHT = 100
IMAGE_WIDTH = 100
COLORS_NUMBER = 3
COLOR_SCHEMA = 'RGBA'


class SetupEnvMixin:
    """
    Helpers for setting up testing environment
    """

    def prepare_environment(self):
        """
        Create keys and image.
        Encrypt private key with AWS KMS and save to S3
        Encrypt image with public key and save to S3
        """
        self.raw_image = self._generate_random_byte_data()
        private_key, public_key = generate_pgp_key_pair()
        self.pgp_s3_key = self.prepare_key(str(private_key))
        self.image_s3_key, self.encrypted_image = \
            self.prepare_image(
                io.BytesIO(self.raw_image), public_key)

    def prepare_key(self, private_key):
        """
        Put encrypted private PGP key to bucket
        """
        private_key_encrypted = encrypt_with_kms(private_key)
        return self._save_key_to_bucket(
            private_key_encrypted)

    def prepare_image(self, jpeg_image_file, pgp_key):
        """
        Put pgp encrypted image to bucket
        """
        encrypted_image = encrypt_file_with_pgp(jpeg_image_file, pgp_key)
        image_bucket = self._save_image_to_bucket(
            encrypted_image)
        return (image_bucket, encrypted_image)

    def _generate_random_byte_data(self):
        return generate_random_string().encode()


    def _save_key_to_bucket(self, data):
        return store_data_at_s3(
            io.BytesIO(data), settings.PGP_KEY_BUCKET, 'test-gpg-keys')

    def _save_image_to_bucket(self, data):
        return store_data_at_s3(
            io.BytesIO(data), settings.IMAGE_BUCKET, 'test-image')


class BaseTestCase(
        SetupEnvMixin, TestCase):
    """
    Base test case class for image testing
    """

    def setUp(self):
        self.prepare_environment()
        self.mock_pgp_key_bucket_in_settings()

    def mock_pgp_key_bucket_in_settings(self):
        from aws_test.apps.api.models import settings
        settings.PGP_S3_KEY = self.pgp_s3_key

    def construct_image_url(self):
        return '/image/%s' % self.image_s3_key


class PGPKeyTest(BaseTestCase):
    """
    Test data can be decrypted
    """

    def test_decrypt_data(self):
        decrypted_image = PGPKey().decrypt_data(self.encrypted_image)
        self.assertEqual(
            decrypted_image, self.raw_image)

    @skip(TEST_NOT_IMPLEMENTED_WARNING)
    def test_key_not_found(self):
        """
        Test proper behaviour if s3 bucket with key could not be found
        """

    @skip(TEST_NOT_IMPLEMENTED_WARNING)
    def test_could_not_decrypt_with_kms(self):
        """
        Test proper behavious if KMS can't decrypt key
        """

    @skip(TEST_NOT_IMPLEMENTED_WARNING)
    def test_could_not_construct_key(self):
        """
        Test proper behavious if key can't be constructed by pgp lib
        """


class SaveImageTest(BaseTestCase):
    """
    Test image can be retrievedand decrypted
    """

    def test_retrieve_image(self):
        image = SafeImage(self.image_s3_key).retrieve()
        self.assertEqual(
            image, self.raw_image)

    @skip(TEST_NOT_IMPLEMENTED_WARNING)
    def test_image_not_found(self):
        """
        Test proper behaivour if image does not exist
        """

    @skip(TEST_NOT_IMPLEMENTED_WARNING)
    def test_image_not_decrypted(self):
        """
        Test proper behaviour if image was not decrypted
        """


class SaveImageViewTest(BaseTestCase):
    """
    Test image can be retrieved from endpoint with valid content type
    """

    def get_image_by_api(self):
        """
        Wrapper for our image api endpoint
        """
        from django.test import Client

        client = Client()
        return client.get(
            self.construct_image_url())

    @patch('aws_test.apps.api.views.HttpResponse')
    def test__retrieve_image_by_api__check_content(self, http_response_mock):
        """
        Test valid image returned
        """
        # not to crash the view
        from django.http import HttpResponse
        http_response_mock.return_value = HttpResponse('Test')

        self.get_image_by_api()
        args, _ = http_response_mock.call_args
        image_passed_as_content = args[0]
        self.assertEqual(
            image_passed_as_content, bytearray(self.raw_image))

    def test__retrieve_image_by_api__check_content_type(self):
        """
        Test valid content type returned
        """
        response = self.get_image_by_api()
        self.assertEqual(
            response['Content-Type'], SafeImage.DEFAULT_CONTENT_TYPE)
