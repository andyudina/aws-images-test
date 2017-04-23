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
