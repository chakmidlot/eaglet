import logging
import shutil
from pathlib import Path
from threading import Thread

from eaglet.storage.notifications import Notificator

logger = logging.getLogger(__name__)


class Folder(Thread):

    daemon = True

    def __init__(self, listening, destination, ciphering):
        self.listening = Path(listening).expanduser()
        self.destination = Path(destination).expanduser()
        self.ciphering = ciphering

        super().__init__()

    def run(self):
        for file in self.listening.iterdir():
            if not file.is_dir():
                self.copy(file.name)

        Notificator().notify(str(self.listening), self.copy)

    def copy(self, name):
        tmp_name = f'.{name}.__siphering_tmp'
        tmp_path = self.destination / tmp_name
        self.ciphering(self.listening / name, tmp_path)
        shutil.move(str(tmp_path), str(self.destination / name))
