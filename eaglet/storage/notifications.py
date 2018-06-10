import logging
import re

import inotify.adapters
from inotify.constants import IN_CLOSE_WRITE, IN_MOVED_TO, IN_MOVED_FROM, IN_ISDIR

logger = logging.getLogger(__name__)


class Notificator():

    PATTERN = re.compile('.(.*).__siphering_tmp')

    def __init__(self):
        self.moves = {}

    def notify(self, path, callback):
        i = inotify.adapters.Inotify()

        i.add_watch(path)

        for event in i.event_gen(yield_nones=False):
            logger.debug(event)
            mask = event[0].mask
            if mask & IN_MOVED_FROM:
                match = self.PATTERN.match(event[3])
                if match:
                    self.moves[match.groups()[0]] = event[0].cookie

            if (
                    mask & IN_CLOSE_WRITE
                    or (mask & IN_MOVED_TO and self.moves.get(event[3]) != event[0].cookie)
            ) and not event[3].startswith('.') and not mask & IN_ISDIR:
                callback(event[3])
