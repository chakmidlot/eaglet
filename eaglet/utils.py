import logging
from pathlib import Path

from eaglet.ciphering import get_sha_hash


def files_same(file_a, file_b):
    a = Path(file_a)
    b = Path(file_b)

    if not a.exists() or not b.exists():
        return False

    return a.read_bytes() == b.read_bytes()


def configure_logging(level):
    rootLogger = logging.getLogger(__package__)
    rootLogger.setLevel(level)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    rootLogger.addHandler(console)


def is_password_valid(password, decrypted_folder):
    password_hash_path = Path(decrypted_folder) / '.config/password_hash'
    password_hash = get_sha_hash(password.encode())
    if not password_hash_path.exists():
        password_hash_path.write_text(password_hash)
        return True

    existing_hash = password_hash_path.read_text()
    return existing_hash == password_hash
