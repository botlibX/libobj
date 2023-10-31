# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212


"locate objects"


from obj.spec import Storage, find, keys


def fnd(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in Storage.files()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no objects in store")
        return
    otype = event.args[0]
    if event.gets:
        args = keys(event.gets)
    else:
        args = None
    clz = Storage.long(otype)
    if "." not in clz:
        for fnm in Storage.files():
            claz = fnm.split(".")[-1]
            if otype == claz.lower():
                clz = fnm
    nmr = 0
    for fnm, obj in find(clz, event.gets):
        event.reply(f"{nmr} {fmt(obj, args)}")
        nmr += 1
    if not nmr:
        event.reply("no result")
