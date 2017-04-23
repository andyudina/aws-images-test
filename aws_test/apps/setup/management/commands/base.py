import boto3
from django.core.management.base import BaseCommand

from aws_test.utils import generate_random_string


class VerboseMixin:
    """
    Helper for verbose messages in management commands
    """

    def __init__(self, *args, **kwargs):
        self._verbose = False
        return super(VerboseMixin, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        """
        Add "verbose" argument support
        """
        parser.add_argument(
            '--verbose',
            dest='verbose',
            default=False,
            help='Show debug messages')

    def verbose(self, msg):
        if not self._verbose:
            return
        print(msg)


class S3StoreMixin:
    """
    Helper for storing data to s3
    """

    def __init__(self, *args, **kwargs):
        self.s3 = boto3.client('s3')
        return super(S3StoreMixin, self).__init__(*args, **kwargs)

    def store_data_at_s3(self, data, bucket, key_prefix):
        """
        Generate random key 
        Store data at s3 bucket with it.
        """
        s3_data_key = '%s-%s' % (
            key_prefix,
            generate_random_string(length=10))
        self.s3.upload_fileobj(
            data, bucket, s3_data_key)
        return s3_data_key


class BaseSetupCommand(
        S3StoreMixin, VerboseMixin, BaseCommand):
    """
    Helper for setup commands
    Responsible for proper constructor calls
    """

    def __init__(self, *args, **kwargs):
        S3StoreMixin.__init__(self, *args, **kwargs)
        return VerboseMixin.__init__(self, *args, **kwargs)
