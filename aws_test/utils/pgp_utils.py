"""PGP related utils"""
from datetime import timedelta

import pgpy


def generate_pgp_key_pair():
    """
    Helper for generating pgp private/public key.
    Return tuple (private_key, public_key)
    """

    private_key = pgpy.PGPKey.new(
        pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    private_key_uid = pgpy.PGPUID.new('Image Test')

    private_key.add_uid(private_key_uid,
                        usage={pgpy.constants.KeyFlags.EncryptStorage},
                        hashes=[
                            pgpy.constants.HashAlgorithm.SHA512],
                        ciphers=[
                            pgpy.constants.SymmetricKeyAlgorithm.AES256],
                        key_expires=timedelta(days=365))
    return (private_key, private_key.pubkey)


def construct_private_key_from_str(private_key_str):
    """
    Wrapper on pgpy api. Constructs key from given str
    """
    key, _ = pgpy.PGPKey.from_blob(private_key_str)
    return key


def encrypt_file_with_pgp(file_obj, pgp_key):
    """
    Encrypt data file obj with pgp key.
    Returns bytes.
    """
    file_bytes = _get_bytes_from_obj(file_obj)
    message = pgp_key.encrypt(
        pgpy.PGPMessage.new(file_bytes, cleartext=False))
    return str(message).encode()


def decrypt_file_with_pgp(file_obj, pgp_key):
    """
    Decrypt data file obj with pgp key.
    Returns bytes.
    """
    file_bytes = _get_bytes_from_obj(file_obj)
    return decrypt_with_pgp(file_bytes, pgp_key)


def decrypt_with_pgp(file_bytes, pgp_key):
    """
    Decrypt given bytes with pgp_key
    Return bytes.
    """
    pgp_message = pgpy.PGPMessage()
    pgp_message.parse(file_bytes)
    message = pgp_key.decrypt(pgp_message)
    return message.message


def _get_bytes_from_obj(file_obj):
    """
    Helper for getting bytes from file obect
    """
    try:
        return file_obj.read()
    except AttributeError:
        raise TypeError('Need file obj with read interface')
