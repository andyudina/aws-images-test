from aws_test.apps.api.models import SafeImage


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
    return _success(image=image)


def _error(error_msg):
    """
    Helper for fromating error message
    """
    return {
        'errorMessage': '[Bad Request] %s' % error_msg
    }


def _success(**kwargs):
    """
    Helper for fromating success message.
    TODO: How can I pass valid content-type?
    """
    return {
        **kwargs
    }
