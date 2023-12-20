# This file is placed in the Public Domain.
#
# pylint: disable=C,R,W0105,E0402,W0611


"directory of objects"


import datetime
import os
import time


from .  import Object, cdir, fqn, items, update
from .  import read, write


from .utility import fntime, strip


def __dir__():
    return (
        'Storage',
    )


__all__ = __dir__()


class Storage(Object):

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
    def fns(mtc) -> []:
        dname = ''
        pth = Storage.store(mtc)
        for rootdir, dirs, _files in os.walk(pth, topdown=False):
            if dirs:
                for dname in sorted(dirs):
                    if dname.count('-') == 2:
                        ddd = os.path.join(rootdir, dname)
                        fls = sorted(os.listdir(ddd))
                        for fll in fls:
                            yield strip(os.path.join(ddd, fll))

    @staticmethod
    def long(name) -> str:
        split = name.split(".")[-1].lower()
        res = name
        for named in Storage.classes:
            if split in named.split(".")[-1].lower():
                res = named
                break
        if "." not in res:
            for fnm in Storage.files():
                claz = fnm.split(".")[-1]
                if fnm == claz.lower():
                    res = fnm
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
