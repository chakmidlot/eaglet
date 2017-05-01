import argparse
import logging
import shutil
import tempfile
from abc import ABCMeta, abstractmethod
from pathlib import Path
from threading import Thread

import pyinotify

from ciphering import encrypt, get_password_hash, decrypt, get_sha_hash


class StorageHandler(pyinotify.ProcessEvent, metaclass=ABCMeta):

    move_destination: Path = None

    def process_IN_CLOSE_WRITE(self, event):
        path = Path(event.pathname)

        self.copy(path)

    @abstractmethod
    def ciphering_stuff(self, path: Path):
        return b''

    def copy(self, path):
        if not self.filtered_out(path):

            logging.info(f'Saving to {self.move_destination / path.name}')

            name = path.name
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            ciphering_result = self.ciphering_stuff(path)
            open(temp_file.name, 'wb').write(ciphering_result)

            replacement_path = self.move_destination / name

            if not files_same(temp_file.name, replacement_path):
                shutil.move(temp_file.name, str(replacement_path))
            else:
                logging.info(f'Files are same')
        else:
            logging.info('Filtered out')

    def filtered_out(self, path):
        if path.is_dir() or str(path).startswith('.'):
            return True

        return False


class DecryptedStorageHandler(StorageHandler):

    @property
    def move_destination(self):
        return encrypted_folder

    def ciphering_stuff(self, path):
        return encrypt(open(path, 'rb').read(), password)


class EncryptedStorageHandler(StorageHandler):
    @property
    def move_destination(self):
        return decrypted_folder

    def ciphering_stuff(self, path):
        return decrypt(path.open('rb').read(), password)


class Notifier(Thread):

    def __init__(self, handler, folder):
        super().__init__()
        self.folder = folder
        self.handler = handler

    def run(self):
        mask = pyinotify.IN_CLOSE_WRITE  # watched events
        wm = pyinotify.WatchManager()

        handler = self.handler()
        notifier = pyinotify.Notifier(wm, handler)

        wm.add_watch(str(self.folder.absolute()), mask, rec=True)
        notifier.loop()


def synchronize():
    decripted_files = [x.name for x in decrypted_folder.iterdir() if not x.is_dir() and not str(x).startswith('.')]
    encrypted_files = [x.name for x in encrypted_folder.iterdir() if not x.is_dir() and not str(x).startswith('.')]

    for file_path in set(decripted_files).intersection(encrypted_files):
        if (decrypted_folder / file_path).stat().st_mtime >= (encrypted_folder / file_path).stat().st_mtime:
            DecryptedStorageHandler().copy(decrypted_folder / file_path)
        else:
            EncryptedStorageHandler().copy(encrypted_folder / file_path)

    for file_path in set(decripted_files).difference(encrypted_files):
        DecryptedStorageHandler().copy(decrypted_folder / file_path)

    for file_path in set(encrypted_files).difference(decripted_files):
        EncryptedStorageHandler().copy(encrypted_folder / file_path)


def files_same(file_a, file_b):
    a = Path(file_a)
    b = Path(file_b)

    if not a.exists() or not b.exists():
        return False

    return a.read_bytes() == b.read_bytes()


def configure_logging():
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    rootLogger.addHandler(console)


def is_password_valid():
    password_hash_path = decrypted_folder / '.config/password_hash'
    password_hash = get_sha_hash(password)
    if not password_hash_path.exists():
        password_hash_path.write_text(password_hash)
        return True

    existing_hash = password_hash_path.read_text()
    return existing_hash == password_hash


def main():
    init()
    logging.info('Checking password')
    if is_password_valid():
        logging.info('Synchronization')
        synchronize()

        logging.info('Monitoring')
        Notifier(DecryptedStorageHandler, decrypted_folder).start()
        Notifier(EncryptedStorageHandler, encrypted_folder).start()
    else:
        logging.error('Password is invalid')


def init():
    encrypted_folder.mkdir(parents=True, exist_ok=True)
    (decrypted_folder / '.config').mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--password', required=True,
                        help='password for ciphering')
    parser.add_argument('-d', '--decrypted-folder', required=True,
                        help='path to a folder with decrypted data')
    parser.add_argument('-e', '--encrypted-folder', required=True,
                        help='path to a folder with encrypted data')

    args = parser.parse_args()
    password = get_password_hash(args.password)

    encrypted_folder = Path(args.encrypted_folder)
    decrypted_folder = Path(args.decrypted_folder)

    configure_logging()

    main()
