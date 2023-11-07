# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402,R0903,E0401,W0105


"log text"


import time


from ..objects import Object
from ..storage import find, fntime, laps, sync


"log"


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


"command"


def log(event):
    if not event.rest:
        nmr = 0
        for fnm, obj in find('log'):
            lap = laps(time.time() - fntime(fnm))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply('no log')
        return
    obj = Log()
    obj.txt = event.rest
    sync(obj)
    event.reply('ok')
