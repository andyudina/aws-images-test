import io

import boto3
from django.core.management.base import BaseCommand

from aws_test import settings
from aws_test.utils import \
    generate_pgp_key_pair, \
    save_str_to_file, \
    encrypt_with_kms, \
    store_data_at_s3
from .base import BaseSetupCommand


class Command(BaseSetupCommand):
    """
    Creates pgp key pair, encrypts pgp private key pair with KMS
    And uploads it to the server
    """

    help = """Generate pgp key pair, encrypt private key with AWS KMS
           and save to S3 bucket"""

    def handle(self, *args, **options):
        self._verbose = options['verbose']
        private_key, public_key = generate_pgp_key_pair()
        self.store_public_key_local(str(public_key))
        self.store_private_key_aws(str(private_key))

    def store_public_key_local(self, public_key):
        """
        Store public key as a ascii file
        """
        save_str_to_file(
            str(public_key),
            settings.PGP_PUBLIC_KEY_FILEPATH)

    def store_private_key_aws(self, private_key):
        """
        Encrypt private key with kms ans store to S3
        """
        private_key_encrypted = encrypt_with_kms(private_key)
        gpg_bucket_key = store_data_at_s3(
            io.BytesIO(private_key_encrypted),
            settings.PGP_KEY_BUCKET, 'gpg-key')
        self.stdout.write(gpg_bucket_key)

