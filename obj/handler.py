# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402,W0718,W0212,W0613,W0702


"handler"


import inspect
import queue
import threading
import _thread


from obj import Default, Object


def __dir__():
    return (
            'Broker',
            'Event',
            'Handler',
           )


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self.channel = ""
        self.orig    = ""
        self.result  = []
        self.txt     = ""

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self) -> None:
        for txt in self.result:
            Broker.say(self.orig, self.channel, txt)


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cmds    = Object()
        self.queue   = queue.Queue()
        self.stopped = threading.Event()
        Broker.add(self)

    def add(self, func) -> None:
        setattr(self.cmds, func.__name__, func)

    def announce(self, txt) -> None:
        self.raw(txt)

    def dosay(self, channel, txt) -> None:
        self.raw(txt)

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
        func = getattr(self.cmds, evt.cmd, None)
        if not func:
            return
        func(evt)
        evt.show()

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

    def raw(self, txt) -> None:
        pass

    def start(self) -> None:
        self.loop()

    def stop(self) -> None:
        self.stopped.set()


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
