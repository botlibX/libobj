# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,E0402,C0209,R1710,C0413


"locate"


__author__ = "libbot <libbotx@gmail.com>"


"imports"


import os
import time


from .object import Default, update
from .method import fqn, search
from .disk   import Storage, fetch, strip


"defines"


def __dir__():
    return (
        "find",
        "fns",
        "fntime",
        "last"
    )


"utilities"


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    clz = Storage.long(mtc)
    for fnm in sorted(fns(clz), key=fntime):
        obj = Default()
        fetch(obj, fnm)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield (fnm, obj)


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


def fntime(daystr) -> float:
    daystr = daystr.replace('_', ':')
    datestr = ' '.join(daystr.split(os.sep)[-2:])
    if '.' in datestr:
        datestr, rest = datestr.rsplit('.', 1)
    else:
        rest = ''
    timed = time.mktime(time.strptime(datestr, '%Y-%m-%d %H:%M:%S'))
    if rest:
        timed += float('.' + rest)
    else:
        timed = 0
    return timed


"methods"


def last(obj, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    if result:
        inp = result[-1][-1]
        update(obj, inp)
