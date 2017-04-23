import random
import string

import pgpy


def generate_random_string(length=10):
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(length))


def generate_pgp_key_pair():
    """
    Helper for generating pgp private/public key.
    Return tuple (private_key, public_key)
    """
    from datetime import timedelta

    private_key = pgpy.PGPKey.new(
        pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    private_key_uid = pgpy.PGPUID.new('Image Test')

    private_key.add_uid(private_key_uid, 
        usage={pgpy.constants.KeyFlags.EncryptStorage}, 
        hashes=[
            pgpy.constants.HashAlgorithm.SHA512, 
            pgpy.constants.HashAlgorithm.SHA256],
        ciphers=[
            pgpy.constants.SymmetricKeyAlgorithm.AES256, 
            pgpy.constants.SymmetricKeyAlgorithm.Camellia256],
        compression=[
            pgpy.constants.CompressionAlgorithm.BZ2, 
            pgpy.constants.CompressionAlgorithm.Uncompressed],
        key_expires=timedelta(days=365))
    return (private_key, private_key.pubkey)


def save_str_to_file(str_to_save, file_path):
    """
    Helper for saving str to file
    """
    with open(file_path, 'w') as f:
        f.write(str_to_save)
