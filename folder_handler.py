import logging
import shutil
import tempfile
from abc import ABCMeta, abstractmethod
from pathlib import Path
from threading import Thread

import pyinotify

from ciphering import encrypt, decrypt
from utils import files_same


class StorageHandler(pyinotify.ProcessEvent, metaclass=ABCMeta):

    move_destination: Path = None
    password = None

    def my_init(self, move_destination=None, password=None):
        self.move_destination = move_destination
        self.password = password

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

    def ciphering_stuff(self, path):
        return encrypt(open(path, 'rb').read(), self.password)


class EncryptedStorageHandler(StorageHandler):

    def ciphering_stuff(self, path):
        return decrypt(path.open('rb').read(), self.password)


class Notifier(Thread):

    def __init__(self, handler, folder):
        super().__init__()
        self.folder = folder
        self.handler = handler

    def run(self):
        mask = pyinotify.IN_CLOSE_WRITE  # watched events
        wm = pyinotify.WatchManager()

        notifier = pyinotify.Notifier(wm, self.handler)

        wm.add_watch(str(self.folder.absolute()), mask, rec=True)
        notifier.loop()
