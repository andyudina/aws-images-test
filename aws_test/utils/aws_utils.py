"""AWS wrappers"""

import boto3


s3 = boto3.client('s3')
kms = boto3.client('kms')


def download_data_from_s3(bucket, key):
    """
    Wrapper for downloading data from s3 bucket
    """
    response = s3.get_object(
        Bucket=bucket, Key=key)
    return response['Body'].read()


def decrypt_with_kms(data):
    """
    Wrapper around boto3 decrypt method
    """
    response = kms.decrypt(
        CiphertextBlob=data)
    return response['Plaintext']
