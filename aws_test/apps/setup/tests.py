"""
Simple tests set for setu env management commands.
Doing basic smoke-like checks that everything is working as expected
(And completely omits checks of behaviour in non-expected cases.)
"""
import io
from unittest.mock import patch

import boto3
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
import pgpy

from aws_test import settings
from aws_test.utils import generate_random_string, \
    generate_pgp_key_pair, \
    save_str_to_file


class UploadImageTest(TestCase):
    """
    Test upload_image management command.
    Check that image is encrypted and uploaded successfully
    """

    def setUp(self):
        """
        Generate dummy public key file and image file in /tmp dif
        """
        # set up aws client
        self.s3 = boto3.client('s3')

        # generate raw data to store
        self.raw_data = generate_random_string(length=20)
        self.data_file = self.get_full_path(
            'data-%s' % generate_random_string(length=10))
        save_str_to_file(
            self.raw_data, self.data_file)

        # generate key pair
        (self.pgp_private_key, self.pgp_public_key) = \
            generate_pgp_key_pair()
        public_key_str_repr = str(self.pgp_public_key)
        self.pgp_key_file = self.get_full_path(
            'pgp-key-%s' % generate_random_string(10))
        save_str_to_file(
            public_key_str_repr, self.pgp_key_file)

    def get_full_path(self, file_name):
        """
        Helper for construction full path to file in tmp directory
        """
        import os
        return os.path.join('/tmp', file_name)

    def run_upload_image_command(self, **kwargs):
        """
        Helper for running upload image command
        """
        call_command('upload_image', 
            self.data_file, self.pgp_key_file, **kwargs)

    @patch('aws_test.apps.setup.management.commands.'\
           'upload_image.Command.store_data_at_s3')
    def test_image_is_encrypted(self, store_data_at_s3_mock):
        """
        Test that file to be stored in s3 bucket 
        is encrypted with given pgp key.
        """
        # disable side effects
        store_data_at_s3_mock.return_value = 'Test'
        self.run_upload_image_command()
        self.assertTrue(
            store_data_at_s3_mock.called)
        args, _ = store_data_at_s3_mock.call_args
        encrypted_data = args[0]
        decrypted_message = self.pgp_private_key.decrypt(
            encrypted_data)
        self.assertEqual(
            self.raw_data, decrypted_message.message)


    @patch('aws_test.apps.setup.management.commands.'\
           'upload_image.Command.encrypt_image')
    def test_file_is_successfully_stored(self, encrypt_image_mock):
        """
        Test that file is successfully stored in S3 and can be retrieved
        """
        # disable side effects
        # shouldn't fail here if encryption doesn't work
        STR_TO_STORE = b'Test'
        encrypt_image_mock.return_value = io.BytesIO(STR_TO_STORE)
        # catch output
        out = StringIO()
        self.run_upload_image_command(stdout=out)
        # get data from bucket
        s3_key = out.getvalue().strip()
        response = self.s3.get_object(
            Bucket=settings.IMAGE_BUCKET,
            Key=s3_key)
        self.assertEqual(
            response['Body'].read(), STR_TO_STORE)
    

class SetupKeysTest(TestCase):
    """
    Test setup_keys management command
    Check that keys is uploaded successfully
    """

    def test_encrypt_with_kms(self):
        """
        Test pgp key are encrypted successfully.
        Encrypt key with kms, then decrypt and compare
        """

    def test_private_key_is_succesfully_stored(self):
        """
        Test that key file is successfully stored in S3 and can be retrieved
        """

    def test_public_key_is_successfully_stored(self):
        """
        Test that public key is successfully stored locally
        """
