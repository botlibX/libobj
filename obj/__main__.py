# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212


"program"


import inspect
import os
import sys
import termios
import time


from .objects import Object
from .runtime import Broker, Reactor, Storage
from .runtime import Censor, Cfg, Commands, Default, Errors, Event
from .runtime import forever, parse,  lsmod, scan


"defines"


Cfg.name   = "obj"
Storage.wd = os.path.expanduser("~/.obj")


"modules"

import obj as mods


"cli"


class CLI(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", Commands.dispatch)

    def announce(self, txt):
        pass

    def dispatch(self, evt):
        Commands.dispatch(evt)

    def dosay(self, channel, txt):
        print(txt.encode('utf-8', 'replace').decode())
        sys.stdout.flush()


"console"


class Console(CLI):


    def poll(self) -> Event:
        evt = Event()
        evt.orig = object.__repr__(self)
        evt.txt = input("> ")
        evt.type = "command"
        return evt


"utilities"
        

def wrap(func) -> None:
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


"runtime"


def main():
    Censor.output = print
    parse(Cfg, " ".join(sys.argv[1:]))
    if "wd" in Cfg.sets:
        Storage.wd = Cfg.wd
    if not Cfg.mod:
        Cfg.mod = ",".join((lsmod(mods.__path__[0])))
    if "v" in Cfg.opts:
        dte = time.ctime(time.time()).replace("  ", " ")
        print(f"{Cfg.name.upper()} started {dte} {Cfg.opts.upper()} {Cfg.mod.upper()}")
    for mod in scan(mods, Cfg.mod):
        if "i" in Cfg.opts and "init" in dir(mod):
            mod.init()
    if "c" in Cfg.opts:
       csl = Console()
       csl.start()
       forever()
       return
    cli = CLI()
    evn = Event()
    evn.orig = object.__repr__(cli)
    evn.txt = Cfg.otxt
    parse(evn)
    cli.dispatch(evn)


if __name__ == "__main__":
    wrap(main)
    Errors.show()
