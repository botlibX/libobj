# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212,E0402
# pylint: disable=W0105,R1710,W0718,W0702


"runtime"


import inspect
import io
import os
import queue
import time
import threading
import traceback
import _thread


"defines"


def __dir__():
    return (
        'Censor',
        'Errors',
        'debug'
    )


from .broker import Broker
from .error  import Errors
from .object import Default, Object, spl
from .disk   import Storage
from .thread import launch


"defines"


def __dir__():
    return (
        'Broker',
        'Censor',
        'Cfg',
        'Commands',
        'Errors',
        'Event',
        'Reactor',
        'debug',
        'lsmod',
        'parse',
        'scan'
    )


Cfg = Default()


"broker"


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


"censor"


class Censor(Object):

    output = None
    words = []

    @staticmethod
    def skip(txt) -> bool:
        for skp in Censor.words:
            if skp in str(txt):
                return True
        return False


"commands"


class Commands:

    cmds = Object()

    def __init__(self):
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


"errors"


class Errors(Object):

    errors = []

    @staticmethod
    def add(exc) -> None:
        excp = exc.with_traceback(exc.__traceback__)
        Errors.errors.append(excp)

    @staticmethod
    def format(exc) -> str:
        res = ""
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            res += line + "\n"
        return res

    @staticmethod
    def handle(exc) -> None:
        if Censor.output:
            Censor.output(Errors.format(exc))

    @staticmethod
    def show() -> None:
        for exc in Errors.errors:
            Errors.handle(exc)


"event"


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


"reactor"


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


"utilities"


def debug(txt):
    if Censor.output and not Censor.skip(txt):
        Censor.output(txt)


def forever():
    while 1:
        try:
            time.sleep(1.0)
        except:
            _thread.interrupt_main()


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


"methods"


def parse(obj, txt=None) -> None:
    args = []
    obj.args    = obj.args or []
    obj.cmd     = obj.cmd or ""
    obj.gets    = obj.gets or Default()
    obj.hasmods = obj.hasmod or False
    obj.index   = None
    obj.mod     = obj.mod or ""
    obj.opts    = obj.opts or ""
    obj.result  = obj.reult or []
    obj.sets    = obj.sets or Default()
    obj.otxt    = txt or obj.txt or ""
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            if key in obj.gets:
                val = getattr(obj.gets, key)
                value = val + "," + value
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""
