# This file is placed in the Public Domain.
#
# pylint: disable=C,R,W0105,E0402,W0611


"find objects"


import datetime
import os


from .  import fqn, items, read, update, write


from .default import Default
from .storage import Storage, fntime, strip
from .utility import spl


def __dir__():
    return (
        'find',
        'ident',
        'fetch',
        'last',
        'search',
        'sync'
    )


__all__ = __dir__()


def find(mtc, selector=None, index=None) -> []:
    clz = Storage.long(mtc)
    nr = -1
    for fnm in sorted(Storage.fns(clz), key=fntime):
        obj = Default()
        fetch(obj, fnm)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        nr += 1
        if index is not None and nr != int(index):
            continue
        yield (fnm, obj)


def ident(obj) -> str:
    return os.path.join(
                        fqn(obj),
                        os.path.join(*str(datetime.datetime.now()).split())
                       )



def fetch(obj, pth) -> None:
    pth2 = Storage.store(pth)
    read(obj, pth2)
    return strip(pth)


def last(obj, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        return inp[0]


def search(obj, selector) -> bool:
    res = False
    if not selector:
        return True
    for key, value in items(selector):
        if key not in obj:
            res = False
            break
        for vval in spl(str(value)):
            val = getattr(obj, key, None)
            if str(vval).lower() in str(val).lower():
                res = True
            else:
                res = False
                break
    return res


def sync(obj, pth=None) -> str:
    if pth is None:
        pth = ident(obj)
    pth2 = Storage.store(pth)
    write(obj, pth2)
    return pth
