# This file is placed in the Public Domain.
#
# pylint: disable=W0401,W0614


"specification"


from .locate  import *
from .object  import *
from .storage import *
from .utils   import *


def __dir__():
    return (
        'Object',
        'construct',
        'edit',
        'fqn',
        'ident',
        'keys',
        'read',
        'search',
        'items',
        'update',
        'values',
        'write'
    )
