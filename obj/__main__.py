# This file is placed in the Public Domain.
#
# pylint: disable=C0103,C0115,C0116,C0209,C0413,W0201,R0903,W0212,W0105,W0613


"program"


import os
import sys


from .disk   import Storage
from .object import Default
from .error  import Errors
from .run    import CLI, Commands, Event
from .run    import command, parse,  lsmod, scan


Cfg = Default()
Cfg.name = __file__.rsplit(os.sep, maxsplit=1)[-1].lower()
Storage.wd = os.path.expanduser(f"~/.{Cfg.name}")

class Cli(CLI, Commands):

    def dosay(self, channel, txt):
        print(txt.encode('utf-8', 'replace').decode())
        sys.stdout.flush()


if os.path.exists("mods"):
    sys.path.insert(0, os.getcwd())
    import mods
    Cfg.mod = ",".join((lsmod(mods.__path__[0])))
else:
    mods = None


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "wd" in Cfg.sets:
        Storage.wd = Cfg.wd
    scan(mods)
    command(Cfg.otxt)
    Errors.show()
    