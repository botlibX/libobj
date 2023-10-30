# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212


"mailbox"


import os
import sys


sys.path.insert(0, os.getcwd())


from obj import Default, Object, Storage, find, fmt


Cfg = Default()


class CLI:

    cmds = Object()

    @staticmethod
    def add(func) -> None:
        setattr(CLI.cmds, func.__name__, func)

    @staticmethod
    def dispatch(evt) -> None:
        func = getattr(CLI.cmds, evt.cmd, None)
        if not func:
            return
        func(evt)
        evt.show()


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self.result  = []
        self.txt     = ""

    def reply(self, txt) -> None:
        self.result.append(txt)

    def show(self) -> None:
        for txt in self.result:
            print(txt.encode('utf-8', 'replace').decode())


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


def cmd(event):
    event.reply(",".join(sorted(CLI.cmds)))


def fnd(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in Storage.files()])
        if res:
            event.reply(",".join(res))
        return
    otype = event.args[0]
    clz = Storage.long(otype)
    if "." not in clz:
        for fnm in Storage.files():
            claz = fnm.split(".")[-1]
            if otype == claz.lower():
                clz = fnm
    nmr = 0
    for fnm, obj in find(clz, event.gets):
        event.reply(f"{nmr} {fmt(obj)}")
        nmr += 1
    if not nmr:
        event.reply("no result")


if __name__ == "__main__":
    parse(Cfg, " ".join(sys.argv[1:]))
    CLI.add(cmd)
    CLI.add(fnd)
    evn = Event()
    evn.txt = Cfg.otxt
    parse(evn)
    CLI.dispatch(evn)
