# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,C0209,C0413,W0201,R0903,W0212


"list of commands"





def cmd(event):
    event.reply(",".join(sorted(CLI.cmds)))
