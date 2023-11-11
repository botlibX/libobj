# This file is placed in the Public Domain.
#
# pylint: disable=E0603,E0402,W0401,W0614


"the python3 bot namespace"


from .disk   import *
from .error  import *
from .object import *
from .run    import *
from .thread import *

def __dir__():
    return (
        'Broker',
        'Censor',
        'Commands',
        'Cfg',
        'CLI',
        'Default',
        'Errors',
        'Event',
        'Object',
        'Reactor',
        'Repeater',
        'Storage',
        'Thread',
        'Timer',
        'cdir',
        'command',
        'construct',
        'debug',
        'dump',
        'dumps',
        'edit',
        'fetch',
        'find', 
        'fmt',
        'fns',
        'fntime', 
        'forever',
        'fqn',
        'hook',
        'ident',
        'items',
        'keys',
        'laps',
        'last',
        'launch',
        'load',
        'loads',
        'lock',
        'lsmod',
        'name',
        'parse',
        'read',
        'scan',
        'search',
        'spl',
        'strip',
        'sync',
        'update',
        'values',
        'write'
    )
