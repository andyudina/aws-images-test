"""
Simple tests set for setu env management commands.
Doing basic smoke-like checks that everything is working as expected
(And completely omits checks of behaviour in non-expected cases.)
"""
import io
from unittest import TestCase
from unittest.mock import patch, MagicMock

import boto3
from django.core.management import call_command
from django.utils.six import StringIO

from aws_test import settings
from aws_test.utils import generate_random_string, \
    generate_pgp_key_pair, \
    save_str_to_file, \
    download_data_from_s3, \
    decrypt_with_kms, \
    decrypt_file_with_pgp


class UploadImageTest(TestCase):
    """
    Test upload_image management command.
    Check that image is encrypted and uploaded successfully
    """

    def setUp(self):
        """
        Generate dummy public key file and image file in /tmp dif
        """
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

    @patch('aws_test.apps.setup.management.commands.'
           'upload_image.store_data_at_s3')
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
        # get encrypted message
        args, _ = store_data_at_s3_mock.call_args
        encrypted_data = args[0]
        # try decrypt message
        decrypted_message = \
            decrypt_file_with_pgp(
                encrypted_data, # store_data_at_s3 accepts file obj
                self.pgp_private_key)
        # check data was correctly encrypted
        self.assertEqual(
            self.raw_data, decrypted_message)

    @patch('aws_test.apps.setup.management.commands.'
           'upload_image.encrypt_file_with_pgp')
    def test_file_is_successfully_stored(self, encrypt_file_with_pgp_mock):
        """
        Test that file is successfully stored in S3 and can be retrieved
        """
        # disable side effects
        # shouldn't fail here if encryption doesn't work
        STR_TO_STORE = b'Test'
        encrypt_file_with_pgp_mock.return_value = STR_TO_STORE
        # catch output
        out = StringIO()
        self.run_upload_image_command(stdout=out)
        # get data from bucket
        s3_key = out.getvalue().strip()
        stored_data = download_data_from_s3(
            settings.IMAGE_BUCKET, s3_key)
        # check data stored successfully
        self.assertEqual(
            stored_data, STR_TO_STORE)


class SetupKeysTest(TestCase):
    """
    Test setup_keys management command
    Check that keys is uploaded successfully
    """

    def setUp(self):
        self.test_private_key = 'Test private'
        self.test_public_key = 'Test public'
        # patch keys generation
        self.patch_key_generator()
        self.addCleanup(
            self.generate_gpg_keys_patcher.stop)

    def patch_key_generator(self):
        self.generate_gpg_keys_patcher = patch(
            'aws_test.apps.setup.management.commands.'
            'setup_keys.generate_pgp_key_pair')
        self.generate_gpg_keys_mock = self.generate_gpg_keys_patcher.start()
        self.generate_gpg_keys_mock.return_value = \
            return_value=(self.test_private_key, self.test_public_key)

    def run_setup_keys_command(self, **kwargs):
        """
        Helper for running setup_keys command
        """
        call_command('setup_keys', **kwargs)

    @patch('aws_test.apps.setup.management.commands.'
           'setup_keys.Command.store_public_key_local')
    @patch('aws_test.apps.setup.management.commands.'
           'setup_keys.store_data_at_s3')
    def test_encrypt_with_kms(self,
                              store_data_at_s3_mock, 
                              store_public_key_local_mock):
        """
        Test pgp key are encrypted successfully.
        Encrypt key with kms, then decrypt and compare
        """
        # disable not needed side effects
        store_public_key_local_mock.return_value = None
        # needs smth printable to stdout
        store_data_at_s3_mock.return_value = ''

        self.run_setup_keys_command()
        # check store was called
        self.assertTrue(
            store_data_at_s3_mock.called)
        args, _ = store_data_at_s3_mock.call_args
        # check encrypted data can be decrypted
        # and is equal decrypted provate key
        encrypted_data = args[0]
        # store_data accepts BytesIO obj
        decrypted_data = decrypt_with_kms(
            encrypted_data.read())
        # data is returned in binary format
        self.assertEqual(
            decrypted_data, self.test_private_key.encode())

    @patch('aws_test.apps.setup.management.commands.'
           'setup_keys.Command.store_public_key_local')
    @patch('aws_test.apps.setup.management.commands.'
           'setup_keys.encrypt_with_kms')
    def test_private_key_is_succesfully_stored(
            self, encrypt_with_kms_mock, store_public_key_local_mock):
        """
        Test that key file is successfully stored in S3 and can be retrieved
        """
        # disable side effects
        store_public_key_local_mock.return_value = None
        encrypt_with_kms_mock.return_value = \
            self.test_private_key.encode()
        # catch output
        out = StringIO()
        self.run_setup_keys_command(stdout=out)
        s3_key = out.getvalue().strip()
        # check data is saved to s3
        stored_key = download_data_from_s3(
            settings.PGP_KEY_BUCKET, s3_key)
        # data is returned in binary format
        self.assertEqual(
            stored_key, self.test_private_key.encode())

    @patch('aws_test.apps.setup.management.commands.'
           'setup_keys.Command.store_private_key_aws')
    def test_public_key_is_successfully_stored(
            self, store_private_key_aws_mock):
        """
        Test that public key is successfully stored locally
        """
        # disable side effects
        store_private_key_aws_mock.return_value = None
        self.run_setup_keys_command()
        # checked key is saved locally
        with open(settings.PGP_PUBLIC_KEY_FILEPATH, 'r') as key_file:
            self.assertEqual(
                key_file.read(), self.test_public_key)
