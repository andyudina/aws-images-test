import io

import pgpy

from aws_test import settings
from aws_test.utils import \
    store_data_at_s3, \
    encrypt_file_with_pgp
from .base import BaseSetupCommand

class Command(
        BaseSetupCommand):
    """
    Encrypt image with pgp key and upload result to S3 bucket.
    Accepts PGP key file and image file as an arguments.
    Then encrypts image with given key and uploads to predefined bucket 
    in settings
    """

    help = "Encrypt image with pgp public key and upload result to S3 bucket"

    def add_arguments(self, parser):
        # necessary args
        parser.add_argument(
            'image', type=str,
            help='Path to image file')
        parser.add_argument(
            'pgp_key', type=str,
            help='Path to pgp public key path')
        # optional args
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        self._verbose = options['verbose']
        self.verbose('Load pgp key')
        pgp_key_file, _ = pgpy.PGPKey.from_file(
            options['pgp_key'])

        self.verbose('Encrypt image')
        with open(options['image'], 'r') as image_file:
            encrypted_image = encrypt_file_with_pgp(
                image_file, pgp_key_file)
        self.verbose('Store image in s3')
        s3_bucket_key = store_data_at_s3(
            io.BytesIO(encrypted_image), 
            settings.IMAGE_BUCKET, 'image')
        self.stdout.write(s3_bucket_key)
