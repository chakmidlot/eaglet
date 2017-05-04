import argparse
import logging
from pathlib import Path

from ciphering import get_password_hash
from folder_handler import DecryptedStorageHandler, EncryptedStorageHandler, Notifier
from initialize import synchronize, init_folder
from utils import configure_logging, is_password_valid


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--password', required=True,
                        help='password for ciphering')
    parser.add_argument('-d', '--decrypted-folder', required=True,
                        help='path to a folder with decrypted data')
    parser.add_argument('-e', '--encrypted-folder', required=True,
                        help='path to a folder with encrypted data')

    return parser.parse_args()


def main():
    init_folder(decrypted_folder, encrypted_folder)
    logging.info('Checking password')
    if is_password_valid(password, decrypted_folder):
        decrypted_storage = DecryptedStorageHandler(move_destination=encrypted_folder, password=password)
        encrypted_storage = EncryptedStorageHandler(move_destination=decrypted_folder, password=password)
        logging.info('Synchronization')
        synchronize(decrypted_storage, encrypted_storage, decrypted_folder, encrypted_folder)

        logging.info('Monitoring')
        Notifier(decrypted_storage, decrypted_folder).start()
        Notifier(encrypted_storage, encrypted_folder).start()
    else:
        logging.error('Password is invalid')


if __name__ == '__main__':
    args = parse_args()

    password = get_password_hash(args.password)

    encrypted_folder = Path(args.encrypted_folder)
    decrypted_folder = Path(args.decrypted_folder)

    configure_logging()

    main()
