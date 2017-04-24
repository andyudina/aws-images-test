from aws_test.apps.api.models import SafeImage


SUCCESS_STATUS_CODE = 200


def get_image(event, context):
    """
    Lambda hadler for retrieving image.
    Expects s3 bucket key to be passed at event['bucket_key'].
    """
    try:
        bucket_key = event['bucket_key']
    except KeyError:
        return _error('No bucket key')
    image = SafeImage(bucket_key).retrieve()
    return _success_image(image)


def _error(error_msg):
    """
    Helper for fromating error message
    """
    return {
        'errorMessage': '[Bad Request] %s' % error_msg
    }


def _success_image(image):
    """
    Helper for fromating success message.
    TODO: How can I pass valid content-type?
    """
    return {
        'statusCode': SUCCESS_STATUS_CODE,
        'headers': {
            'Content-Type': SafeImage.DEFAULT_CONTENT_TYPE},
        'image': image
    }
