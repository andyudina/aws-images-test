from botocore.exceptions import ClientError

from aws_test.apps.api.models import SafeImage
from aws_test.utils import bytes_to_base64_str


SUCCESS_STATUS_CODE = 200
NON_AUTHORIZED_STATUS_CODE = 401
BAD_REQUEST_ERROR = 400

def get_image(event, context):
    """
    Lambda hadler for retrieving image.
    Expects s3 bucket key to be passed at event['pathParameters']['bucket_key'].
    And session key in headers event['headers']['s3-session-token']
    """
    try:
        bucket_key = event['pathParameters']['bucket_key']
    except KeyError:
        return _bad_request_error('No bucket key')
    try:
        session_token= event['headers']['s3-session-token']
        access_key_id = event['headers']['s3-access-key-id']
        secret_access_key = event['headers']['s3-access-key']
    except KeyError:
        return _non_authorized_error(
            'Not enough credentials to authorize')
    try:
        image = SafeImage(
            session_token=session_token,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key).retrieve(bucket_key)
    except ClientError as e:
        # TODO: log here
        print(e)
        return _non_authorized_error(
            'Invalid credentials')
    return _success_image(image)


def _bad_request_error(error_msg):
    """
    Helper for formating bad request error message
    """
    return _error(error_msg, BAD_REQUEST_ERROR)

def _non_authorized_error(error_msg):
    """
    Helper for formating non authorized error message
    """
    return _error(error_msg, NON_AUTHORIZED_STATUS_CODE)

def _error(error_msg, status_code):
    """
    Helper for formatting error message
    """
    return {
        'statusCode': status_code,
        'body': error_msg}

def _success_image(image):
    """
    Helper for fromating success message.
    TODO: How can I pass valid content-type?
    """
    image_base64 = bytes_to_base64_str(image)
    return {
        'statusCode': SUCCESS_STATUS_CODE,
        'headers': {
            'Content-Type': SafeImage.DEFAULT_CONTENT_TYPE},
        'image': image_base64
    }
