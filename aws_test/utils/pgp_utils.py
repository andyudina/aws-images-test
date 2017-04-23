"""PGP related utils"""

import pgpy


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


def construct_private_key_from_str(self, private_key_str):
    """
    Wrapper on pgpy api. Constructs key from given str
    """
    key, _ = pgpy.PGPKey.from_blob(private_key_str)
    return key

