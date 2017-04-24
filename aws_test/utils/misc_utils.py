"""
Miscelaneous utils
"""
import random
import string


def generate_random_string(length=10):
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(length))


def save_str_to_file(str_to_save, file_path):
    """
    Helper for saving str to file
    """
    with open(file_path, 'w') as f:
        f.write(str_to_save)


def to_bytes(data):
    """
    Graceful (kind of) convertation to bytes
    Accepts str or bytes data
    """
    assert(
        isinstance(data, str) or isinstance(data, bytes),
        'Data should be bytes or str')

    if isinstance(data, str):
        return data.encode()
    else:
        return data
