# This file is placed in the Public Domain.
#
# pylint: disable=C,R,W0212,E0402,W0105 W0718,W0702,E1102,W0246


"runtime"


import inspect
import os
import queue
import threading
import time
import types
import _thread


from obj.disk   import Storage
from obj.error  import Errors
from obj.object import Default, Object, spl
from obj.parse  import parse


def __dir__():
    return (
        'Broker',
        'Censor',
        'Cfg',
        'Commands',
        'Errors',
        'Event',
        'Reactor',
        'command',
        'debug',
        'lsmod',
        'scan'
    )


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready  = threading.Event()
        self._thrs   = []
        self.orig    = None
        self.result  = []
        self.txt     = ""

    def ready(self):
        self._ready.set()

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self) -> None:
        for txt in self.result:
            Broker.say(self.orig, self.channel, txt)

    def wait(self):
        for thr in self._thrs:
            thr.join()
        self._ready.wait()
        return self.result


class Broker(Object):

    objs = []

    @staticmethod
    def add(obj) -> None:
        Broker.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        for obj in Broker.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig) -> Object:
        for obj in Broker.objs:
            if object.__repr__(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(obj) -> None:
        try:
            Broker.objs.remove(obj)
        except ValueError:
            pass

    @staticmethod
    def say(orig, channel, txt) -> None:
        bot = Broker.byorig(orig)
        if not bot:
            return
        bot.dosay(channel, txt)


class Commands(Object):

    cmds = Object()

    def __init__(self):
        Object.__init__(self)
        Broker.add(self)

    @staticmethod
    def add(func) -> None:
        setattr(Commands.cmds, func.__name__, func)

    def announce(self, txt):
        pass

    @staticmethod
    def dispatch(evt) -> None:
        parse(evt)
        func = getattr(Commands.cmds, evt.cmd, None)
        if not func:
            return
        try:
            func(evt)
            evt.show()
        except Exception as exc:
            Errors.add(exc)

    def dosay(self, txt):
        raise NotImplementedError("Commands.dosay")

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)


class Reactor(Object):

    def __init__(self):
        Object.__init__(self)
        self.cbs     = Object()
        self.queue   = queue.Queue()
        self.stopped = threading.Event()
        Broker.add(self)

    def dispatch(self, evt) -> None:
        func = getattr(self.cbs, evt.type, None)
        if not func:
            evt.ready()
            return
        evt._thr = launch(func, evt)

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.dispatch(self.poll())
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self) -> Event:
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def register(self, typ, cbs) -> None:
        setattr(self.cbs, typ, cbs)

    def start(self) -> None:
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()


class CLI(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", Commands.dispatch)

    def announce(self, txt):
        pass

    def dispatch(self, evt):
        Commands.dispatch(evt)

    def dosay(self, channel, txt):
        raise NotImplementedError("CLI.dosay")


def command(txt, clt=None):
    cli = clt or CLI()
    evn = Event()
    evn.orig = object.__repr__(cli)
    evn.txt = txt
    parse(evn)
    cli.dispatch(evn)
    return evn


def lsmod(path) -> []:
    if not os.path.exists(path):
        return {}
    for fnm in os.listdir(path):
        if not fnm.endswith(".py"):
            continue
        if fnm in ["__main__.py", "__init__.py"]:
            continue
        yield fnm[:-3]


def scan(pkg, mnames=None) -> []:
    res = []
    if not pkg:
        return res
    if mnames is None:
        mnames = ",".join(lsmod(pkg.__path__[0]))
    for mname in spl(mnames):
        module = getattr(pkg, mname, None)
        if not module:
            continue
        Commands.scan(module)
        Storage.scan(module)
        res.append(module)
    return res
