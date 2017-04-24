"""
Functional tests for AWS handler
FIXME: add wrong arguments tests too
Now we chek only best-case scenario
Shouldn't be always so
"""
import unittest

from aws_test.apps.api.tests import BaseTestCase

from aws_lambda.handler import get_image


class ImageLambdaHandlerTest(BaseTestCase):
    """
    Test image can be retrieved by handler
    """

    def construct_event_for_handler(self):
        return {
            'bucket_key': self.image_s3_key
        }

    def construct_context_for_handler(self):
        # Not used yet
        return {}

    def test_retrieve_image__success(self):
        """
        Test expected image returned
        """
        response = get_image(
            self.construct_event_for_handler(),
            self.construct_context_for_handler())
        self.assertEqual(
            response['image'],
            self.raw_image)

    def test_retrieve_image__not_passed_bucket_key(self):
        """
        Test client error returned
        """
        # Lambda sets error code by checking response to regex
        response = get_image(
            {}, self.construct_context_for_handler())
        self.assertIn(
            'Bad Request',
            response['errorMessage'])


if __name__ == '__main__':
    unittest.main()
