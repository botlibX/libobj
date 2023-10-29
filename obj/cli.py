# This file is placed in the Public Domain.
#
#


"command line interface"


import os
import queue
import sys
import threading
import time
import _thread


sys.path.insert(0, os.getcwd())


from .object  import Default, Object
from .storage import Storage


def __dir__():
    return (
            'Broker',
            'Event',
            'Handler',
           )


Cfg = Default()


class CLI(Object):

    def __init__(self):
        Object.__init__(self)
        self.cmds    = Object()
        Broker.add(self)

    def add(self, func) -> None:
        setattr(self.cmds, func.__name__, func)

    def announce(self, txt) -> None:
        self.raw(txt)

    def dosay(self, channel, txt) -> None:
        self.raw(txt)

    def event(self, txt):
        evt = Event()
        evt.txt = txt
        evt.orig = object.__repr__(self)
        return evt

    def dispatch(self, evt) -> None:
        func = getattr(self.cmds, evt.cmd, None)
        if not func:
            return
        func(evt)
        evt.show()

    def poll(self):
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def raw(self, txt) -> None:
        pass


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


def parse(obj, txt=None) -> None:
    args = []
    obj.args    = obj.args or []
    obj.cmd     = obj.cmd or ""
    obj.gets    = obj.gets or Default()
    obj.hasmods = obj.hasmod or False
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
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
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
    