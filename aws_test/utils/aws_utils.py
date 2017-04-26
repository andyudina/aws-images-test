"""AWS wrappers"""

import boto3

from .misc_utils import generate_random_string


s3 = boto3.client('s3')
kms = boto3.client('kms')


def store_data_at_s3(data_fileobj, bucket, key_prefix):
    """
    Generate random key
    Store data at s3 bucket with it.
    """
    s3_data_key = '%s-%s' % (
        key_prefix,
        generate_random_string(length=10))
    s3.upload_fileobj(
        data_fileobj, bucket, s3_data_key)
    return s3_data_key


def download_data_from_s3(bucket, key, **kwargs):
    """
    Wrapper for downloading data from s3 bucket.
    WARNING: access to images should be provided only for
    valid session keys (incapsulated in image_s3_client)
    """
    s3_client = kwargs.get('s3_client', s3)
    response = s3_client.get_object(
        Bucket=bucket, Key=key)
    return response['Body'].read()


def decrypt_with_kms(data):
    """
    Wrapper around boto3 decrypt method
    """
    _test_data_can_be_used_with_kms(data)
    response = kms.decrypt(
        CiphertextBlob=data)
    return response['Plaintext']


def encrypt_with_kms(data):
    """
    Wrapper for boot3 KMS encryption api
    """
    from aws_test import settings

    _test_data_can_be_used_with_kms(data)
    response = kms.encrypt(
        KeyId=settings.KMS_KEY_ID,
        Plaintext=data)
    return response['CiphertextBlob']


def _test_data_can_be_used_with_kms(data):
    """
    Asserts if data has compatible with KMS API type
    """
    assert \
        isinstance(data, bytes) or isinstance(data, str), \
        'Data should be string or bytes type'
