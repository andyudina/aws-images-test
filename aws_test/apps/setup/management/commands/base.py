import boto3
from django.core.management.base import BaseCommand

from aws_test.utils import generate_random_string


class VerboseMixin(object):
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


class BaseSetupCommand(
        VerboseMixin, BaseCommand):
    """
    Helper for setup commands
    Responsible for proper constructor calls
    """
    pass
