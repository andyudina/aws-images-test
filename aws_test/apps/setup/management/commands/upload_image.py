import pgpy

from aws_test import settings
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
        encrypted_image = self.encrypt_image(
            options['image'], pgp_key_file)
        self.verbose('Store image in s3')
        s3_bucket_key = self.store_data_at_s3(
            encrypted_image, settings.IMAGE_BUCKET, 'image')
        self.stdout.write(s3_bucket_key)

    def encrypt_image(self, image_file_path, pgp_key):
        """
        Encrypt image with pgp key from file
        """
        return pgp_key.encrypt(
            pgpy.PGPMessage.new(image_file_path, file=True))

