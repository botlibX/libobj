# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,E0402,C0209,R1710


"storage"


import datetime
import inspect
import os


from .object import Object, cdir, items, read, write


def  __dir__():
    return (
            'Storage',
            'edit',
            'fetch',
            'fqn',
            'ident',
            'sync'
           )


class Storage:

    classes = {}
    wd = ""

    @staticmethod
    def add(clz) -> None:
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Storage.classes[name] = clz

    @staticmethod
    def files() -> []:
        return os.listdir(Storage.store())

    @staticmethod
    def long(name) -> str:
        split = name.split(".")[-1].lower()
        res = name
        for named in Storage.classes:
            if split in named.split(".")[-1].lower():
                res = named
                break
        return res

    @staticmethod
    def mods() -> str:
        pth =  Storage.path("mods")
        cdir(pth)
        return pth

    @staticmethod
    def path(pth) -> str:
        if not pth:
            pth = ""
        pth2 =  os.path.join(Storage.wd, pth)
        cdir(pth2)
        return pth2

    @staticmethod
    def store(pth="") -> str:
        pth = os.path.join(Storage.wd, "store", pth)
        pth2 = os.path.dirname(pth)
        cdir(pth2)
        return pth

    @staticmethod
    def scan(mod) -> None:
        for key, clz in inspect.getmembers(mod, inspect.isclass):
            if key.startswith("cb"):
                continue
            if not issubclass(clz, Object):
                continue
            Storage.add(clz)


"utilities"


def strip(pth) -> str:
    return os.sep.join(pth.split(os.sep)[-3:])


"methods"


def edit(obj, setter, skip=False) -> None:
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            obj[key] = int(val)
            continue
        except ValueError:
            pass
        try:
            obj[key] = float(val)
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            obj[key] = True
        elif val in ["False", "false"]:
            obj[key] = False
        else:
            obj[key] = val


def fqn(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def ident(obj) -> str:
    return os.path.join(
                        fqn(obj),
                        os.path.join(*str(datetime.datetime.now()).split())
                       )


def fetch(obj, pth) -> None:
    pth2 = Storage.store(pth)
    read(obj, pth2)
    return strip(pth)


def sync(obj, pth=None) -> str:
    if pth is None:
        pth = ident(obj)
    pth2 = Storage.store(pth)
    write(obj, pth2)
    return pth