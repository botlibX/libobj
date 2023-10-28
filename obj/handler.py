# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402,W0718,W0212,W0613,W0702


"handler"


import inspect
import queue
import threading
import _thread


from .       import Object
from .event  import Event
from .thread import launch


def __dir__():
    return (
            'Handler',
           )


class Handler(Object):

    cmds = {}

    def __init__(self):
        Object.__init__(self)
        self.cbs     = Object()
        self.queue   = queue.Queue()
        self.stopped = threading.Event()
        self.end     = threading.Event()

    @staticmethod
    def add(func) -> None:
        Handler.cmds[func.__name__] = func

    def event(self, txt) -> Event:
        evt = Event()
        evt.txt = txt
        evt.orig = object.__repr__(self)
        return evt

    def forever(self) -> None:
        try:
            self.stopped.wait()
        except:
            _thread.interrupt_main()

    def dispatch(self, evt) -> None:
        func = getattr(self.cbs, evt.type, None)
        if not func:
            evt.ready()
            return
        evt._thr = launch(func, self, evt)

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

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Handler.add(cmd)

    def register(self, typ, cbs) -> None:
        setattr(self.cbs, typ, cbs)

    def start(self) -> None:
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.register("command", command)

    def announce(self, txt) -> None:
        self.raw(txt)

    def dosay(self, channel, txt) -> None:
        self.raw(txt)

    def raw(self, txt) -> None:
        pass


class CLI(Client):

    def announce(self, txt):
        pass

    def raw(self, txt):
        cprint(txt)


def command(bot, evt) -> None:
    func = Handler.cmds.get(evt.cmd, None)
    if not func:
        evt.ready()
        return
    try:
        evt._bot = bot
        func(evt)
        evt.show()
    except Exception as ex:
        Errors.add(ex)
    evt.ready()
