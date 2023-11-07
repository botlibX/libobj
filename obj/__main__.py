# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212,W0105,W0613


"program"


import getpass
import inspect
import os
import pwd
import sys
import termios
import time


from .objects import Object, cdir
from .runtime import Broker, Reactor, Storage
from .runtime import Censor, Cfg, Commands, Default, Errors, Event
from .runtime import debug, forever, parse,  lsmod, scan


import obj


"defines"


Cfg.name    = __file__.split(os.sep)[-2].lower()
Storage.wd = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Storage.wd, f"{Cfg.name}.pid")
Cfg.user    = getpass.getuser()


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


def daemon(pidfile, verbose=False):
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 != 0:
        os._exit(0)
    if not verbose:
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as sos:
            os.dup2(sos.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as ses:
            os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    if os.path.exists(pidfile):
        os.unlink(pidfile)
    cdir(os.path.dirname(pidfile))
    with open(pidfile, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def privileges(username):
    pwnam = pwd.getpwnam(username)
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)


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
    parse(Cfg, " ".join(sys.argv[1:]))
    if "v" in Cfg.opts:
        dte = time.ctime(time.time()).replace("  ", " ")
        print(f"{Cfg.name.upper()} started {dte} {Cfg.opts.upper()} {Cfg.mod.upper()}")
        print(Cfg.pidfile)
    if not Cfg.mod:
        Cfg.mod = ",".join((lsmod(obj.__path__[0])))
    if "d" in Cfg.opts:
        daemon(Cfg.pidfile, "v" in Cfg.opts)
        privileges(Cfg.user)
        for mod in scan(obj, Cfg.mod):
            if "init" in dir(mod):
                mod.init()
        forever()
        return
    Censor.output = print
    if "wd" in Cfg.sets:
        Storage.wd = Cfg.wd
    for mod in scan(obj, Cfg.mod):
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
