# This file is placed in the Public Domain,
#
#


"utilities"


import os
import pathlib


def __dir__():
    return (
        "cdir",
    )    


__all__ = __dir__()


def cdir(pth) -> None:
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)
